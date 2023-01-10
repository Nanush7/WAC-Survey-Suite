"""
Survey response validator.
"""
from re import sub
from sys import exit as sysexit

import pandas


class Validator:
    """
    Main class
    """

    WCA_TOKEN_FIELD = 'wca_token'
    WCA_TOKEN_LEN = 64
    DATE_FIELD = 'Start Date'
    # DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'
    MAX_COLUMNS = 400

    def __init__(self, arguments, logger) -> None:
        self.logger = logger
        self.input_path = arguments.input_file
        self.tokens_path = arguments.tokens
        self.token_list = []
        self.output_path = arguments.output_file
        self.dry_run = arguments.dry_run
        self.total_responses = -1
        self.deleted = 0

    def run(self):
        self.logger.lverbose('Opening files...')

        # Survey responses.
        try:
            # All the data will be a string to avoid Pandas adding floating points.
            self.df = pandas.read_csv(self.input_path, converters={
                                             i: str for i in range(self.MAX_COLUMNS)})
        except FileNotFoundError:
            self.logger.lerr('Survey file not found.')
            sysexit(1)

        # Tokens.
        with open(self.tokens_path, 'r') as f:
            self.token_list = f.read().split('\n')

        # Start validation.
        self.total_responses = len(self.df) - 1

        bad_token_column = self.df.columns[-1]

        # Delete responses with duplicated tokens.
        self.logger.linfo('Removing responses with duplicated tokens...')
        previous_amount = len(self.df)
        self.delete_older_duplicates()
        new_amount = len(self.df)
        duplicates_deleted = previous_amount - new_amount
        self.deleted += duplicates_deleted
        self.logger.linfo(f'Removed {duplicates_deleted} duplicates.')

        self.logger.linfo('Validating responses...')

        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Fix tokens placed in an incorrect column.
            if not token and len(row[bad_token_column]) == self.WCA_TOKEN_LEN:
                token = row[bad_token_column].strip()
                row[self.WCA_TOKEN_FIELD] = token

            # Delete responses with invalid tokens.
            if not self.delete_invalid(token) or not token:
                self.logger.linfo(f'#{index} >> Invalid token')
                self._delete(index)
                continue

            self.logger.lverbose(f'#{index} >> OK')

        if not self.dry_run:  # TODO: lista de índices a eliminar.
            # Remove bad_token_column from dataframe.
            if not self.df[bad_token_column].empty:
                self.logger.lerr('bad_token_column is not empty. Dropping anyway...')
            self.df.drop([bad_token_column], axis=1)

            # Write data to csv file.
            self.df.to_csv(self.output_path, sep=',', index=False, encoding='utf-8')

            # Pandas adds "Unnamed: ..." to columns without a name.
            # We have to remove that.
            self.logger.linfo('Fixing header...')
            Validator.fix_headers(self.output_path)

    def delete_invalid(self, token: str) -> bool:  # TODO: Eliminar acá.
        """
        Check if the token is valid and delete the response if not.
        """
        return token in self.token_list

    def delete_older_duplicates(self) -> None:
        """
        Take all the repeated tokens and delete all, except the newest one.
        """
        self.df.drop_duplicates(subset=[self.WCA_TOKEN_FIELD], keep='first', ignore_index=False, inplace=True)

    def _delete(self, index: int) -> None:
        """
        Delete dataframe row.
        """
        self.logger.lverbose(f'#{index} >> deleted')
        self.df.drop(index, axis=0, inplace=True)
        self.deleted += 1

    @staticmethod
    def fix_headers(file_path: str) -> None:
        """
        Remove "Unnamed: ..." from column headers.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = sub(r'(Unnamed: )[0-9]+', '', content)

        # Write fixed content.
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
