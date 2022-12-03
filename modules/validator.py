"""
Survey response validator.
"""
import csv
from os import devnull
from tqdm import tqdm
from sys import exit as sysexit

class Validator:
    """
    Main class
    """

    WCA_TOKEN_FIELD='WCA_token'

    def __init__(self, arguments, logger) -> None:
        self.logger = logger
        if arguments.dry_run:
            self.input_path = devnull
        else:
            self.input_path = arguments.input_file
        self.input_path = arguments.input_file
        self.tokens_path = arguments.tokens
        self.output_path = arguments.output_file
        self.token_list = []


    def run(self):
        self.logger.lverbose('Opening files...')

        # Survey responses.
        try:
            input_file = open(self.input_path, 'r', newline='')
        except FileNotFoundError:
            self.logger.lerr('Survey file not found.')
            sysexit(1)

        reader = csv.DictReader(input_file)
        self.data_as_str = input_file.read()

        # Tokens.
        with open(self.tokens_path, 'r') as f:
            self.token_list = f.read().split('\n')

        # Validated file.
        output_file = open(self.output_path, 'w')
        writer = csv.writer(output_file)

        # Copy meta fields to the new file.
        writer.writerows([next(reader), next(reader)])

        # Start validation.
        repeated_tokens = []

        self.logger.linfo('Validating responses...')
        for response in tqdm(reader):
            token = response[self.WCA_TOKEN_FIELD]

            # Check if the token was already found as repeated.
            if token in repeated_tokens:
                self.logger.lwarn(f'#{reader.line_num} >> Token repeated.')
                continue

            # Check if the token is valid.
            if not self.check_valid(token):
                self.logger.lwarn(f'#{reader.line_num} >> Invalid token.')
                continue

            # Check if the token is repeated.
            if self.check_unique(token, reader):
                self.logger.lwarn(f'#{reader.line_num} >> Token repeated << {token}.')
                repeated_tokens.append(token)
                continue

            self.logger.lverbose(f'#{reader.line_num} >> OK.')
            writer.writerow(response)

        input_file.close()
        output_file.close()


    def check_unique(self, token: str, csv_reader) -> bool:
        """
        Check if the token is repeated.
        """
        # occurrences = self.data_as_str.count(token)
        # return occurrences > 1
        count = 0
        for row in csv_reader:
            # FIXME: Debug.
            print(row)
            if row[self.WCA_TOKEN_FIELD] == token:
                count += 1

        return count > 1

    def check_valid(self, token: str) -> bool:
        """
        Check if the token is valid.
        """
        return token in self.token_list
