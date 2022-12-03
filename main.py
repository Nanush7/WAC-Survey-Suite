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
    general.add_argument('input_file', required=True, help='Plain text file with the tokens')
    general.add_argument('tokens', required=True, help='Tokens file')
    general.add_argument('--dry-run', help='Do not generate the validated file', dest='dry_run')
    general.add_argument('-o', '--output', help='File with the valid responses', dest='output_file', default='validated.csv')

    log.add_argument('--no-info', help='Do not show info messages',
                             dest='info', action='store_false')
    log.add_argument('v', '--verbose', help='Show debug messages', action='store_true')
    log.add_argument('--log-file', help='Log Output to output.log', action='store_true', dest='logfile')
    log.add_argument('--no-colors', help='Disable colored logs', action='store_false', dest='nocolors')

    args = parser.parse_args()

    # Log options.
    log_config = {
        'info': args.info,
        'verbose': args.verbose,
        'file': args.logfile,
        'colors': args.colors
    }
    logger = LogWrapper(log_config)

    validator_class = Validator(args, logger)
    validator_class.run()


if __name__ == '__main__':
    main()
