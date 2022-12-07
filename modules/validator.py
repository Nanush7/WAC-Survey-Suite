"""
Survey response validator.
"""
import pandas
from re import sub
from sys import exit as sysexit


class Validator:
    """
    Main class
    """

    WCA_TOKEN_FIELD = 'wca_token'
    MAX_COLUMNS = 100

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
            #  All the data will be a string to avoid Pandas adding floating points.
            self.dataframe = pandas.read_csv(self.input_path, converters={
                                             i: str for i in range(self.MAX_COLUMNS)})
        except FileNotFoundError:
            self.logger.lerr('Survey file not found.')
            sysexit(1)

        # Tokens.
        with open(self.tokens_path, 'r') as f:
            self.token_list = f.read().split('\n')

        # Start validation.
        repeated_tokens = []
        self.total_responses = len(self.dataframe) - 1
        self.deleted = 0

        self.logger.linfo('Validating responses...')
        for index, row in self.dataframe.iloc[1:].iterrows():
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
            if not self.check_unique(token, index):
                self.logger.lwarn(f'#{index} >> Token repeated << {token}')
                repeated_tokens.append(token)
                self._delete(index)
                continue

            self.logger.lverbose(f'#{index} >> OK')

        if not self.dry_run:
            # Pandas adds "Unnamed: .." to columns without a name.
            # We have to remove that.
            self.dataframe.to_csv(self.output_path, sep=',', index=False)
            # Fix the headers.
            self.logger.linfo('Fixing headers...')
            with open(self.output_path, 'r') as f:
                content = f.read()

            content = sub(r'(Unnamed: )+[0-9]*[0-9]*[0-9]', '', content)

            # Write fixed content.
            with open(self.output_path, 'w') as f:
                f.write(content)

    def check_unique(self, token: str, start_index) -> bool:
        """
        Check if the token is repeated.
        """
        duplicate = self.dataframe[self.WCA_TOKEN_FIELD].iloc[start_index+1:].eq(token)
        return not duplicate.any()

    def check_valid(self, token: str) -> bool:
        """
        Check if the token is valid.
        """
        return token in self.token_list

    def _delete(self, index) -> None:
        """
        Delete dataframe row.
        """
        self.dataframe.drop(index, inplace=True)
        self.deleted += 1
