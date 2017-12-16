import array
import pytest
import sys
from synasm import asm


def test_parse_ignores_empty_lines():
    assert list(asm.parse('some\nother')) == ['some', 'other']
    assert list(asm.parse('some\n\n\n\n\nother')) == ['some', 'other']
    assert list(asm.parse('  \n  some  \n  other \n\n')) == ['some', 'other']


def test_parse_strips_comments():
    assert list(asm.parse(';hello')) == []
    assert list(asm.parse('  ;hello ;world')) == []
    assert list(asm.parse('  ;  hello  ')) == []
    assert list(asm.parse('some  ;  hello  ')) == ['some']
    assert list(asm.parse(';hello \n some \n ; world ')) == ['some']
    assert list(asm.parse('some  \';\' arg ; hello')) == ['some  \';\' arg']
    assert list(asm.parse('some  \';\'; hello')) == ['some  \';\'']
    assert list(asm.parse("some 'o;ther' ; ignore")) == ["some 'o;ther'"]


def test_parse_labels():
    assert list(asm.parse('some:')) == [':some']
    assert list(asm.parse('some: other')) == [':some', 'other']
    assert list(asm.parse('some:\n\tother')) == [':some', 'other']
    assert list(asm.parse('some: \t other \t ; \t ignore')) == [':some', 'other']
    assert list(asm.parse('some :here\nhere: other')) == ['some :here', ':here', 'other']


def test_parse_pass_instruction():
    assert list(asm.parse('some instruction')) == ['some instruction']
    assert list(asm.parse('a b  c  d e')) == ['a b  c  d e']
    assert list(asm.parse(r"some 'pa\nram'")) == [r"some 'pa\nram'"]


def test_unescape():
    assert asm.unescape("'some'") == 'some'
    assert asm.unescape(r"'\\'") == '\\'
    assert asm.unescape(r"'\t'") == '\t'
    assert asm.unescape(r"'\r'") == '\r'
    assert asm.unescape(r"'\n'") == '\n'
    assert asm.unescape(r"'a\tr\nz'") == 'a\tr\nz'


def test_assemble_step1_processes_lines():
    assert asm.step1(['some', 'other']) == ['some', 'other']
    assert asm.step1('some\nother') == ['some', 'other']
    assert asm.step1('\n some \n\n \nother\n\n') == ['some', 'other']


def test_assemble_step2_extracts_labels():
    assert asm.step2([':here', 'some']) == (['some'], {':here':0})
    assert asm.step2(['some', ':here']) == (['some'], {':here':1})
    assert asm.step2(['some', ':here', ':more', 'other']) == (['some', 'other'], {':here':1, ':more':1})


def test_assemble_step3_emits_opcodes():
    assert asm.step3((['noop'], {})) == [(21,)]
    assert asm.step3((['mult a b c'], {})) == [(10, 32768, 32769, 32770)]
    assert asm.step3((["out 'x'"], {})) == [(19, ord('x'))]
    assert asm.step3((["out -'x'"], {})) == [(19, -ord('x') % 0x8000)]


def test_assemble_step3_emits_int():
    assert asm.step3((["push 42"], {})) == [(2, 42)]
    assert asm.step3((["push 'A'"], {})) == [(2, ord('A'))]
    assert asm.step3((["push 0x42"], {})) == [(2, 0x42)]


def test_assemble_step3_emits_string():
    assert asm.step3((["out 'hi'"], {})) == [(19, ord('h')), (19, ord('i'))]


def test_assemble_step3_emits_escaped_string():
    assert asm.step3(([r"out 'h\\\t'"], {})) == [(19, ord('h')), (19, ord('\\')), (19, ord('\t'))]


def test_assemble_step3_fixes_labels():
    assert asm.step3((['call :here', 'ret'], {':here': 1})) == [(17, 2), (18,)]
    assert asm.step3((['call :here', 'ret', 'noop'], {':here': 2})) == [(17, 3), (18,), (21,)]
    assert asm.step3((['call :here', 'ret'], {':here': 2})) == [(17, 3), (18,)]

    with pytest.raises(asm.SynasmError):
        asm.step3((['call :here'], {}))


def test_assemble_step4_packs_array():
    assert sys.byteorder == 'little'
    assert asm.step4([(2, 2), (18,)]) == array.array('H', [2, 2, 18])


def test_assemble_pipeline():
    assert asm.assemble('push :here\n ; ignore \n here: ret') == array.array('H', [2, 2, 18])


def test_emit_halt():
    assert list(asm.emit('halt')) == [(0,)]


def test_emit_set():
    assert list(asm.emit('set a b')) == [(1, 32768, 32769)]


def test_emit_push():
    assert list(asm.emit('push c')) == [(2, 32770)]


def test_emit_pop():
    assert list(asm.emit('pop d')) == [(3, 32771)]


def test_emit_eq():
    assert list(asm.emit('eq e f g')) == [(4, 32772, 32773, 32774)]

def test_emit_gt():
    assert list(asm.emit('gt h 2 10')) == [(5, 32775, 2, 10)]


def test_emit_jmp():
    assert list(asm.emit('jmp 8')) == [(6, 8)]
    assert list(asm.emit('jmp :some', labels={':some':2})) == [(6, 2)]


def test_emit_jt():
    assert list(asm.emit('jt c 42')) == [(7, 32770, 42)]


def test_emit_jf():
    assert list(asm.emit('jf d 18')) == [(8, 32771, 18)]


def test_emit_add():
    assert list(asm.emit('add a 2 2')) == [(9, 32768, 2, 2)]


def test_emit_mult():
    assert list(asm.emit('mult a 5 7')) == [(10, 32768, 5, 7)]


def test_emit_mod():
    assert list(asm.emit('mod a 5 7')) == [(11, 32768, 5, 7)]


def test_emit_and():
    assert list(asm.emit('and a 5 7')) == [(12, 32768, 5, 7)]


def test_emit_or():
    assert list(asm.emit('or a 5 7')) == [(13, 32768, 5, 7)]


def test_emit_not():
    assert list(asm.emit('not a 2')) == [(14, 32768, 2)]


def test_emit_rmem():
    assert list(asm.emit('rmem a 42')) == [(15, 32768, 42)]


def test_emit_wmem():
    assert list(asm.emit('wmem 42 a')) == [(16, 42, 32768)]


def test_emit_call():
    assert list(asm.emit('call :some', labels={':some':42})) == [(17, 42)]


def test_emit_ret():
    assert list(asm.emit('ret')) == [(18,)]


def test_emit_out():
    assert list(asm.emit('out 3')) == [(19, 3)]


def test_emit_in():
    assert list(asm.emit('in a')) == [(20, 32768)]


def test_emit_noop():
    assert list(asm.emit('noop')) == [(21,)]


def test_emit_invalid_args():
    with pytest.raises(asm.SynasmError):
        list(asm.emit('jmp'))
    with pytest.raises(asm.SynasmError):
        list(asm.emit('jt'))
    with pytest.raises(asm.SynasmError):
        list(asm.emit('jt 1'))
