from modules.log import LogWrapper
from modules.validator import Validator

import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Script to validate survey tokens.'
    )

    # Argument groups.
    general = parser.add_argument_group(title='General options')
    log = parser.add_argument_group(title='Log options')

    # Arguments.
    general.add_argument('input_file', help='Plain text file with the tokens')
    general.add_argument('tokens', help='Token list file')
    general.add_argument(
        '--dry-run', help='Do not generate the validated file', action='store_true', dest='dry_run')
    general.add_argument('-o', '--output', help='Validated responses',
                         dest='output_file', default='validated.csv')
    general.add_argument('-l',
                         help='Generate a list of responses to delete, instead of generating a validated CSV file.',
                         action='store_true',
                         dest='to_delete_list')  # TODO.

    log.add_argument(
        '-q', '--quiet', help='Do not log anything', action='store_true')
    log.add_argument('--no-warn', help='Do not show warnings',
                     action='store_true', dest='no_warn')
    log.add_argument('-v', '--verbose',
                     help='Show debug messages', action='store_true')
    log.add_argument('--log-file', help='Log Output to output.log',
                     action='store_true', dest='log_file')
    log.add_argument('--no-colors', help='Disable colored logs',
                     action='store_false', dest='no_colors')

    args = parser.parse_args()

    # Validate args.
    if args.quiet and args.verbose:
        parser.error('Cannot use quiet and verbose at the same time.')

    if args.to_delete_list and args.output_file:
        parser.error('Cannot use -o and -l at the same time.')

    # Log options.
    log_config = {
        'verbose': args.verbose,
        'no_warn': args.no_warn,
        'file': args.log_file,
        'colors': args.no_colors
    }
    logger = LogWrapper(log_config, not args.quiet)

    validator_class = Validator(args, logger)
    validator_class.run()
    logger.linfo('Completed.')
    logger.linfo(
        f'Deleted {validator_class.deleted} out of {validator_class.total_responses} responses.')


if __name__ == '__main__':
    main()
