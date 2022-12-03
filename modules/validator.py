"""
Survey response validator.
"""
import csv

class Validator:
    """
    Main class
    """

    def __init__(self, arguments, logger) -> None:
        self.logger = logger
        self.dry = arguments.dry_run
        self.input_file = arguments.input_file
        self.tokens_file = arguments.tokens
        self.output_file = arguments.output_file


    def run(self):
        input_csv = csv.reader(self.input_file)
        with open(self.tokens_file, 'r') as f:
            self.tokens = f.read()
        # validated_csv = csv.writer()


    def check_unique(self):
        """
        Check if the token is repeated.
        """
        pass


    def check_valid(self):
        """
        Check if the token is valid.
        """
        pass


    def check_ip_address(self):
        """
        Check ip address.
        """
        pass
