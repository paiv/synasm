import ast
import array
import base64
import fileinput
import re
import sys


class SynasmError(Exception): pass


token_rx = re.compile(r'^\s*((?:\s*(?:\-?\'(?:\\.|[^\'])+\'|[^\s;]+))*?)\s*(?:;.*?)?\s*$', re.M)
label_rx = re.compile(r'^\s*(\w+\:)?\s*(.*?)\s*$', re.M)

def parse(text):
    for tok in token_rx.findall(text):
        for label,instr in label_rx.findall(tok):
            if label:
                yield ':' + label[:-1]
            if instr:
                yield instr


instr_rx = re.compile(r'^\s*(\w+)(.*?)\s*$')
args_rx = re.compile(r'\s+(\-?\'(?:\\.|[^\'])+\'|[:-]?\w+)')

op_table = {
    # name: code, nargs
    'halt': (0, 0),
    'set': (1, 2),
    'push': (2, 1),
    'pop': (3, 1),
    'eq': (4, 3),
    'gt': (5, 3),
    'jmp': (6, 1),
    'jt': (7, 2),
    'jf': (8, 2),
    'add': (9, 3),
    'mult': (10, 3),
    'mod': (11, 3),
    'and': (12, 3),
    'or': (13, 3),
    'not': (14, 2),
    'rmem': (15, 2),
    'wmem': (16, 2),
    'call': (17, 1),
    'ret': (18, 0),
    'out': (19, 1),
    'in': (20, 1),
    'noop': (21, 0),
}


def unescape(s):
    u = ast.literal_eval(s)
    return u if isinstance(u, str) else s


def emit(asm, labels=None):

    def arg(x):
        if x[0] == '\'':
            assert x[-1] == '\''
            x = unescape(x)
            if len(x) == 1:
                x = ord(x)
            return x
        elif x[0] == ':':
            if labels is not None:
                if x in labels:
                    return labels[x]
                raise SynasmError('{}  label not defined'.format(asm))
            return x
        elif x[:2] == '-\'':
            assert x[3] == '\''
            return -ord(x[2]) % 32768
        elif x.isalpha():
            return ord(x) - ord('a') + 32768
        else:
            return int(x, 0) % 32768


    def explode_str(code, i=1):
        if i >= len(code):
            yield code
        elif isinstance(code[i], str) and code[i][0] != ':':
            for x in code[i]:
                yield from explode_str((*code[:i], ord(x), *code[i+1:]), i + 1)
        else:
            yield from explode_str(code, i + 1)


    name, args = instr_rx.findall(asm)[0]
    args = [arg(x) for x in args_rx.findall(args) if x]

    op, n = op_table[name]
    code = (op, *args[:n])

    if len(code) != n + 1:
        raise SynasmError('{}  {} takes {} arguments'.format(asm, name, n))

    yield from explode_str(code)


def step1(lines):
    if isinstance(lines, str):
        lines = lines.splitlines()

    return list(x for line in lines for x in parse(line))


def step2(ast):
    labels = dict()
    prog = []
    for x in ast:
        if x[0] == ':':
            labels[x] = len(prog)
        else:
            prog.append(x)

    return (prog, labels)


def step3(ast):
    lines, labels = ast

    asm = list(x for line in lines for x in emit(line))

    runlen = []
    size = 0
    for instr in asm:
        runlen.append(size)
        size += len(instr)
    runlen.append(size)
    runlen.append(size)

    labels = {l:runlen[i] for l,i in labels.items()}

    asm = (x for line in lines for x in emit(line, labels))
    return list(filter(None, asm))


def step4(asm):
    raw = array.array('H', (x for instr in asm for x in instr))

    if sys.byteorder != 'little':
        raw.byteswap()

    return raw


def assemble(text, verbose=False):
    ast = step1(text)
    ast = step2(ast)
    raw = step3(ast)

    if verbose:
        sys.stderr.write('{} instructions\n'.format(len(raw)))

    raw = step4(raw)

    if verbose:
        sys.stderr.write('{} bytes\n'.format(len(raw) * raw.itemsize))

    return raw


def assemble_files(files, outfile, encode=False, verbose=False):
    raw = assemble(fileinput.input(files), verbose=verbose)

    if encode:
        s = base64.b64encode(raw.tobytes())
        w = 76
        s = b'\n'.join(s[i:i+w] for i in range(0, len(s), w))
        outfile.write(s + b'\n')
    else:
        raw.tofile(outfile)
