#!/usr/bin/env python

import argparse

from ansipants import ANSIDecoder


parser = argparse.ArgumentParser(description="Convert ANSI art to HTML.")
parser.add_argument('filename')
parser.add_argument(
    '--encoding', default='cp437',
    help="Character encoding of input (default: cp437)"
)
parser.add_argument(
    '--width', type=int, default=80,
    help="Number of columns of output (default: 80)"
)
parser.add_argument(
    '--strict', action='store_true',
    help="Fail loudly on encountering a decoding error"
)
args = parser.parse_args()

with open(args.filename, 'rt', encoding=args.encoding) as f:
    decoder = ANSIDecoder(f, width=args.width, strict=args.strict)

print(decoder.as_html())
