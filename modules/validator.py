"""
Survey response validator.
"""
from datetime import datetime
from sys import exit as sysexit

import pandas

import format


class Validator:
    """
    Main class
    """

    WCA_TOKEN_FIELD = 'wca_token'
    WCA_TOKEN_LEN = 64
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
        except FileNotFoundError:
            self.logger.lerr('Survey file not found.')
            sysexit(1)

        # Tokens.
        with open(self.tokens_path, 'r') as f:
            self.token_list = f.read().split('\n')

        # Start validation.
        self.total_responses = len(self.df) - 1
        self.deleted = 0

        bad_token_column = self.df.columns[-1]

        self.logger.linfo('Validating responses...')
        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Fix tokens placed in an incorrect column.
            if not token and len(row[bad_token_column]) == self.WCA_TOKEN_LEN:
                token = row[bad_token_column].strip()
                row[self.WCA_TOKEN_FIELD] = token

            # Check if the token is valid.
            if not self.check_valid(token) or not token:
                self.logger.lwarn(f'#{index} >> Invalid token')
                self._delete(index)
                continue

            # Check if the token is repeated.
            matching_tokens = self.find_matching_tokens(token, index)
            if len(matching_tokens) > 1:
                self.logger.lwarn(f'{token} >> found {len(matching_tokens)} times')
                # TODO: Ver si hay problema con el desplazamiento de los índices.
                # TODO: Ver si drop borra el índice relativo.
                self.delete_older_repeated(matching_tokens)
                continue

            self.logger.lverbose(f'#{index} >> OK')

        if not self.dry_run:
            # Remove bad_token_column from dataframe.
            self.df.drop([bad_token_column], axis=1)

            # Write data to csv file.
            self.df.to_csv(self.output_path, sep=',', index=False)

            # Pandas adds "Unnamed: ..." to columns without a name.
            # We have to remove that.
            self.logger.linfo('Fixing headers...')
            format.fix_headers(self.output_path)

    def find_matching_tokens(self, token: str, start_index) -> list[int]:
        """
        Check if the token is repeated.
        """
        duplicates = self.df.index[self.WCA_TOKEN_FIELD].iloc[start_index:].eq(token)
        return duplicates

    def check_valid(self, token: str) -> bool:
        """
        Check if the token is valid.
        """
        return token in self.token_list

    def delete_older_repeated(self, to_delete: list[int]) -> None:
        """
        Take all the repeated tokens and delete all but the newest with the same IP address.
        """
        # For some reason, some responses' IP address don't have dots.
        # Remove all dots to compare addresses.
        # ip_address = ip_address.replace('.', '')

        # TODO: ojo iloc.
        # Agarrar la ip de la primera hecha.
        for index, row in to_delete:
            row_date = datetime.strptime(row['Start Date'], '%m/%d/%Y %I:%M:%S %p')
            # if row_date > ...

    def _delete(self, index) -> None:
        """
        Delete dataframe row.
        """
        self.logger.lverbose(f'#{index} >> deleted')
        self.df.drop(index, inplace=True)
        self.deleted += 1

"""
bad_token_column = df.columns[-1]

for index, row in df.iloc[1:].iterrows():
    # Not checking if the token is valid.

    token = row['wca_token'].strip()

    if not token and len(row[bad_token_column].strip()) == 64:
        token = row[bad_token_column].strip()
    if not token:
        # Ignore responses without tokens (for now).
        continue

    duplicates = df['wca_token'].loc[index:].eq(token)
    i_to_check = duplicates.index[duplicates.eq(True)].tolist()

    if len(i_to_check) > 1:
        if all(df.loc[i]['IP Address'] == row['IP Address'] for i in i_to_check):
            repeated_same_ip.append(token)
        else:
            repeated_diff_ip.append(token)

        # Now delete all the responses with that token.
        for i in i_to_check:
            df.drop(i, inplace=True)
"""
