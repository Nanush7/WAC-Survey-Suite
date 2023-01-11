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

    ID_FIELD = 'Respondent ID'
    WCA_TOKEN_FIELD = 'wca_token'
    WCA_TOKEN_LEN = 64
    DATE_FIELD = 'Start Date'
    # DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'
    MAX_COLUMNS = 400

    def __init__(self, arguments, logger) -> None:
        self.logger = logger
        self.tokens_path = arguments.tokens
        self.token_list = []
        self.dry_run = arguments.dry_run
        self.list_only = arguments.list_only
        self.total_responses = -1
        self.deleted = 0
        self.to_delete = pandas.Series(name='Respondent ID', dtype='U')

    def run(self, input_path: str, output_path: str):
        self.logger.lverbose('Opening files...')

        # Survey responses.
        try:
            # All the data will be a string to avoid Pandas adding floating points.
            self.df = pandas.read_csv(input_path, converters={
                                             i: str for i in range(self.MAX_COLUMNS)})
        except FileNotFoundError:
            self.logger.lerr('Survey file not found.')
            sysexit(1)

        # Tokens.
        with open(self.tokens_path, 'r') as f:
            self.token_list = f.read().split('\n')

        self.total_responses = len(self.df) - 1
        self.bad_token_column = self.df.columns[-1]
        # FIXME: Agregar if not bad_token_column = 'Unnamed' para no corregir.

        # Run chosen method.
        if self.list_only:
            self.run_list(output_path)
        else:
            self.run_delete(output_path)

    def run_delete(self, output_path: str):
        """
        The script will run in deletion mode. A clean copy of the CSV file will be generated.
        """
        # Delete responses with duplicated tokens.
        self.logger.linfo('Checking responses with duplicated tokens...')
        previous_amount = len(self.df)
        self.delete_older_duplicates(False)
        new_amount = len(self.df)
        duplicates_deleted = previous_amount - new_amount
        self.deleted += duplicates_deleted
        self.logger.linfo(f'Removed {duplicates_deleted} duplicates.')

        self.logger.linfo('Validating responses...')

        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Fix tokens placed in an incorrect column.
            if not token and len(row[self.bad_token_column]) == self.WCA_TOKEN_LEN:
                token = row[self.bad_token_column].strip()
                row[self.WCA_TOKEN_FIELD] = token

            # Delete responses with invalid tokens.
            if not self.is_valid(token) or not token:
                self.logger.linfo(f'#{index} >> Invalid token')
                self._delete(index)
                continue

            self.logger.lverbose(f'#{index} >> OK')

        if not self.dry_run:
            # Remove bad_token_column from dataframe.
            if not self.df[self.bad_token_column].empty:
                self.logger.lwarn('bad_token_column is not empty. Dropping anyway...')
            self.df.drop([self.bad_token_column], axis=1)

            # Write data to csv file.
            self.df.to_csv(output_path, sep=',', index=False, encoding='utf-8')

            # Pandas adds "Unnamed: ..." to columns without a name.
            # We have to remove that.
            self.logger.linfo('Fixing header...')
            Validator.fix_headers(output_path)

    def run_list(self, output_path):
        """
        The script will run in list mode. A list of responses to delete will be generated.
        """
        # List responses with duplicated tokens.
        self.logger.linfo('Checking responses with duplicated tokens...')
        duplicates = self.delete_older_duplicates(True)
        duplicates_deleted = len(duplicates)
        self.logger.linfo(f'Found {duplicates_deleted} duplicates.')

        # Append to to_delete pandas series.
        self.to_delete.append(self.df[duplicates][self.ID_FIELD])

        self.logger.linfo('Validating responses...')

        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Fix tokens placed in an incorrect column.
            if not token and len(row[self.bad_token_column]) == self.WCA_TOKEN_LEN:
                token = row[self.bad_token_column].strip()
                row[self.WCA_TOKEN_FIELD] = token

            # Check responses with invalid tokens.
            if not self.is_valid(token) or not token:
                self.logger.linfo(f'#{index} >> Invalid token')
                self.to_delete.append(self.df.iloc[index][self.ID_FIELD])  # FIXME.
                continue

            self.logger.lverbose(f'#{index} >> OK')

        # Check bad_token_column.
        if not self.df[self.bad_token_column].empty:
            self.logger.lwarn('bad_token_column is not empty. Dropping anyway...')

        with open(output_path, 'w') as f:
            self.to_delete.to_string(buf=f, dtype='U')

        self.deleted = len(self.to_delete)

    def is_valid(self, token: str) -> bool:  # TODO: Eliminar acá.
        """
        Check if the token is valid and delete the response if not.
        """
        return token in self.token_list

    def delete_older_duplicates(self, list_only: bool = False) -> pandas.Series | None:
        """
        Take the repeated tokens and delete (or list) all, except the newest one.

        :returns: DataFrame with the responses to delete or None if responses where deleted in place.
        """
        if list_only:
            duplicates = self.df.duplicated(subset=[self.WCA_TOKEN_FIELD], keep='first')
            return duplicates
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
