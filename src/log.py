"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
import os
import logging
from colorama import Fore, Back, init


class LogWrapper:
    """Logging wrapper class"""

    def __init__(self, config={}):

        self.verbose = config.get('verbose', False)
        self.warn = not config.get('no_warn', not self.verbose)
        self.file = config.get('file', False)
        self.colors = config.get('colors', True)
        self.enabled = not config.get('quiet', False)

        # Get new logger.
        self.logger = logging.getLogger('main_logger')
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '[%(module)s][%(levelname)s] %(message)s')

        if self.enabled:
            # File Handler.
            if self.file:
                fh = logging.FileHandler('output.log')
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)

            # Console Handler.
            if self.colors:
                init(autoreset=True)
                formatter = _CustomFormatter()

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        else:
            self.logger.disabled = True

    def clear(self) -> None:
        """
        Clear console screen.
        """
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    ##########################
    # Log with level prefix #
    ##########################

    def l_verbose(self, debug_text):
        """Log verbose messages"""
        if self.verbose:
            self.logger.debug(debug_text)

    def l_info(self, info_text):
        """Log execution information."""
        self.logger.info(info_text)

    def l_warning(self, warning):
        """Log warnings."""
        if self.warn:
            self.logger.warning(warning)

    def l_error(self, message):
        """Log errors."""
        self.logger.error(message)

    #####################
    # Print with colors #
    #####################

    def p_red(self, message, end='\n'):
        print(Fore.RED + message, end=end)

    def p_yellow(self, message, end='\n'):
        print(Fore.YELLOW + message, end=end)

    def p_green(self, message, end='\n'):
        print(Fore.LIGHTGREEN_EX + message, end=end)

    def p_blue(self, message, end='\n'):
        print(Fore.BLUE + message, end=end)


class _CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    yellow = Fore.YELLOW
    red = Fore.RED
    reset = Fore.RESET + Back.RESET
    format = "[%(levelname)s] %(message)s"

    FORMATS = {
        logging.INFO: format,
        logging.DEBUG: format,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
