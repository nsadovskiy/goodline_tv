#!/usr/bin/env python3

import configargparse
from goodline_iptv.importer import do_import


if __name__ == '__main__':
    parser = configargparse.ArgParser()

    parser.add_argument('-o', '--out-dir',
                        required=True,
                        env_var='OUTDIR',
                        help='Output directory')

    parser.add_argument('-e', '--encoding',
                        default='cp1251',
                        env_var='ENCODING',
                        help='Source JTV teleguide encoding')

    parser.add_argument('-t', '--timezone',
                        default='+0700',
                        env_var='TIMEZONE',
                        help='Source JTV teleguide timezone')

    parser.add_argument('-u', '--udpxy',
                        env_var='UDPXY_ADDR',
                        help='Address of the udproxy service, if available')

    parser.add_argument('-v', '--verbosity',
                        default=0,
                        env_var='VERBOSITY',
                        type=int, choices=range(0, 4),
                        help='Verbosity level')

    args = parser.parse_args()

    do_import(args.verbosity, args.out_dir, args.encoding, args.timezone, args.udpxy)
