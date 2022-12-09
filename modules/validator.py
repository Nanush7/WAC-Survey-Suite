"""
Survey response validator.
"""
from sys import exit as sysexit

import pandas

import format


class Validator:
    """
    Main class
    """

    WCA_TOKEN_FIELD = 'wca_token'
    MAX_COLUMNS = 200

    def __init__(self, arguments, logger) -> None:
        self.logger = logger
        self.input_path = arguments.input_file
        self.tokens_path = arguments.tokens
        self.token_list = []
        self.output_path = arguments.output_file
        self.dry_run = arguments.dry_run

    def run(self):
        self.logger.lverbose('Opening files...')

        # Survey responses.
        try:
            # All the data will be a string to avoid Pandas adding floating points.
            self.df = pandas.read_csv(self.input_path, converters={
                                             i: str for i in range(self.MAX_COLUMNS)})

            # Some random tokens will be in an incorrect column, fix below.
            self.df = format.fix_token_columns(self.df)
        except FileNotFoundError:
            self.logger.lerr('Survey file not found.')
            sysexit(1)

        # Tokens.
        with open(self.tokens_path, 'r') as f:
            self.token_list = f.read().split('\n')

        # Start validation.
        repeated_tokens = []
        self.total_responses = len(self.df) - 1
        self.deleted = 0

        self.logger.linfo('Validating responses...')
        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Check if the token was already found as repeated.
            if token in repeated_tokens:
                self.logger.lwarn(f'#{index} >> Token repeated')
                self._delete(index)
                continue

            # Check if the token is valid.
            if not self.check_valid(token) or not token:
                self.logger.lwarn(f'#{index} >> Invalid token')
                self._delete(index)
                continue

            # Check if the token is repeated.
            if not self.find_matching_tokens(token, index):
                self.logger.lwarn(f'#{index} >> Token repeated << {token}')
                repeated_tokens.append(token)
                self._delete(index)
                continue

            self.logger.lverbose(f'#{index} >> OK')

        if not self.dry_run:
            # Write data to csv file.
            self.df.to_csv(self.output_path, sep=',', index=False)

            # Pandas adds "Unnamed: .." to columns without a name.
            # We have to remove that.
            self.logger.linfo('Fixing headers...')
            format.fix_headers(self.output_path)

    def find_matching_tokens(self, token: str, start_index) -> list[int]:
        """
        Check if the token is repeated.
        """
        duplicates = self.df.index[self.WCA_TOKEN_FIELD].iloc[start_index + 1:].eq(token)
        return duplicates

    def check_valid(self, token: str) -> bool:
        """
        Check if the token is valid.
        """
        return token in self.token_list

    def delete_oldest_repeated(self) -> None:
        """
        Take all the repeated tokens and delete all but the
        """

    def _delete(self, index) -> None:
        """
        Delete dataframe row.
        """
        self.df.drop(index, inplace=True)
        self.deleted += 1
