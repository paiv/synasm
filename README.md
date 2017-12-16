
paiv – Assembler for Synacor VM (https://challenge.synacor.com/)


Installing
----------

```sh
pip install git+https://github.com/paiv/synasm.git
```

```
usage: synasm [-h] [-o [OUTFILE]] [-b] [-v] [infile [infile ...]]

Synacor VM Assembler

positional arguments:
  infile                assembly file

optional arguments:
  -h, --help            show this help message and exit
  -o [OUTFILE], --outfile [OUTFILE]
                        assembly file
  -b, --base64          encode output in Base64
  -v, --verbose         print details
```


Assembly syntax
---------------

Registers: `a b c d e f g h` (32768..32775)

Basic example:

```asm
out  'Hello, World!\n'
```

Another example:

```asm
  jmp :loop
loop:
  eq c a b
  jf c :loop
  set a 10
  call :some
  out 10
  ret
some:
  jf a :somend
somext:
  out '.'
  add a a -1
  jt a :somext
somend:
  ret
```
