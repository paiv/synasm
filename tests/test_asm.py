import array
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
    # assert list(asm.parse('some  \';\' arg ; hello')) == ['some  \';\' arg']
    # assert list(asm.parse('some  \';\'; hello')) == ['some  \';\'']


def test_parse_labels():
    assert list(asm.parse('some:')) == [':some']
    assert list(asm.parse('some: other')) == [':some', 'other']
    assert list(asm.parse('some:\n\tother')) == [':some', 'other']
    assert list(asm.parse('some: \t other \t ; \t ignore')) == [':some', 'other']
    assert list(asm.parse('some :here\nhere: other')) == ['some :here', ':here', 'other']


def test_parse_pass_instruction():
    assert list(asm.parse('some instruction')) == ['some instruction']
    assert list(asm.parse('a b  c  d e')) == ['a b  c  d e']


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


def test_assemble_step3_fixes_labels():
    assert asm.step3((['push :here', 'ret'], {':here': 1})) == [(2, 2), (18,)]


def test_assemble_step4_packs_array():
    assert sys.byteorder == 'little'
    assert asm.step4([(2, 2), (18,)]) == array.array('H', [2, 2, 18])


def test_assemble_pipeline():
    assert asm.assemble('push :here\n ; ignore \n here: ret') == array.array('H', [2, 2, 18])
