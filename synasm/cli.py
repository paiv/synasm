import argparse
import sys
from .asm import assemble_files


def cli():
    parser = argparse.ArgumentParser(description='Synacor VM Assembler')

    parser.add_argument('infile', nargs='*',
        help='assembly file')
    parser.add_argument('-o', '--outfile', nargs='?', default=sys.stdout.buffer, type=argparse.FileType('wb'),
        help='assembly file')
    parser.add_argument('-b', '--base64', action='store_true',
        help='encode output in Base64')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='print details')

    args = parser.parse_args()

    assemble_files(
        args.infile if args.infile else '-',
        args.outfile,
        encode=args.base64,
        verbose=args.verbose
    )
