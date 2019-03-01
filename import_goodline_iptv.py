#!/usr/bin/env python3

from argparse import ArgumentParser
from goodline_iptv.importer import do_import


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-o', '--out-dir', required=True, help='Output directory')
    parser.add_argument('-e', '--encoding', default='cp1251', help='Source JTV teleguide encoding')
    parser.add_argument('-t', '--timezone', default='+0700', help='Source JTV teleguide timezone')
    parser.add_argument('-p', '--pretty-xmltv', default=False, help='Prettify output xmltv')
    parser.add_argument('-v', '--verbosity', default=0, type=int, choices=range(0, 4), help='Verbosity level')

    args = parser.parse_args()

    do_import(args.verbosity, args.out_dir, args.encoding, args.timezone, args.pretty_xmltv)
