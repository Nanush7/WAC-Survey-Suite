#! /usr/bin/python3
"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""

from src.log import LogWrapper
from src.cli import CLI

import argparse
from os import path


def main():
    parser = argparse.ArgumentParser(
        description='Script to validate survey tokens.'
    )

    # Argument groups.
    general = parser.add_argument_group(title='General options')
    log = parser.add_argument_group(title='Log options')

    # Arguments.
    general.add_argument('-d', '--dir', help='Path to survey CSV directory.', type=str, default=None)

    log.add_argument(
        '-q', '--quiet', help='Do not log anything', action='store_true')
    log.add_argument('--no-warn', help='Do not show warnings',
                     action='store_true', dest='no_warn')
    log.add_argument('-v', '--verbose',
                     help='Show debug messages', action='store_true')
    log.add_argument('-l', '--log-file', help='Log Output to output.log',
                     action='store_true', dest='log_file')
    log.add_argument('--no-colors', help='Disable colored logs',
                     action='store_false', dest='no_colors')

    args = parser.parse_args()

    # Validate args.
    if args.dir:
        if not path.isdir(args.dir):
            parser.error('Directory not found.')

    if args.quiet and args.verbose:
        parser.error('Cannot use quiet and verbose at the same time.')

    # Log options.
    log_config = {
        'verbose': args.verbose,
        'no_warn': args.no_warn,
        'file': args.log_file,
        'colors': args.no_colors,
        'quiet': args.quiet
    }
    logger = LogWrapper(log_config)

    cli_class = CLI(args.dir, logger)
    cli_class.run()


if __name__ == '__main__':
    main()
