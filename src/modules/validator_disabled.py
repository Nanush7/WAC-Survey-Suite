"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
import pandas
import os.path
from re import sub
from src.modules import builder


class Validator(builder.BaseModule):

    # Some settings.
    ID_FIELD = 'Respondent ID'
    WCA_TOKEN_FIELD = 'wca_token'
    WCA_TOKEN_LEN = 64
    DATE_FIELD = 'Start Date'
    # DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'
    MAX_COLUMNS = 400  # FIXME.

    def __init__(self, **kwargs):
        # Add anything you want here.
        name = 'Validator'
        description = 'Validate tokens and remove duplicates.'
        version = '1.0'
        authors = 'Nanush7'
        super().__init__(name, description, version, authors, **kwargs)

        # Stats and other data.
        self.tokens_path = None
        self.token_list = []
        self.list_only = False
        self.total_responses = 0
        self.deleted = 0
        self.to_delete = []
        self.df = None
        self.bad_token_column = None

        # Menu.
        self.main_menu = builder.Menu(extra_start=f'\n{self.name} module v{self.version} by {self.authors}.\n',
                                      back_option=True)

    def startup(self):
        # Survey responses.
        # Load data as string to avoid Pandas adding floating points.
        self.df = pandas.read_csv(self.file, converters={i: str for i in range(self.MAX_COLUMNS)})

        # Tokens.
        self.out.p_blue('Use Ctrl-C to abort setup.')
        try:
            while not self.tokens_path:
                path = input('Path to tokens file: ')
                if os.path.isfile(path):
                    self.tokens_path = path
                else:
                    self.out.p_yellow('File not found, try again.')
        except KeyboardInterrupt:
            return False

        with open(self.tokens_path, 'r') as f:
            self.token_list = f.read().split('\n')

        # Build menu.
        self.main_menu.add_numbered_option('Delete invalid responses from original CSV file.')
        self.main_menu.add_numbered_option('List responses to delete.')

        return True

    def on_file_change(self, file):
        if self.startup_completed:
            self.df = pandas.read_csv(file, converters={i: str for i in range(self.MAX_COLUMNS)})

    def run(self) -> None:
        while True:
            choice = self.main_menu.display()
            if choice == 'back':
                break

            # Reset some attributes on each run.
            self.total_responses = len(self.df) - 1
            self.deleted = 0
            self.to_delete = []
            self.bad_token_column = self.df.columns[-1]
            if 'Unnamed' not in self.bad_token_column:
                self.bad_token_column = None
            if self.bad_token_column:
                self.out.l_warning('Bad Token Column found.')

            # Run option.
            if choice == '1':
                self.run_delete()
            elif choice == '2':
                self.run_list()

            # Print stats.
            self.out.l_info(f'Deleted {self.deleted} out of {self.total_responses} responses.')

    def run_delete(self):
        """
        The script will run in deletion mode. A clean copy of the CSV file will be generated.
        """
        output_path = 'validated_' + self.file.name

        self.out.l_info('Fixing columns...')
        if self.bad_token_column:
            self.fix_token_position()

        # Delete responses with duplicated tokens.
        self.out.l_info('Checking responses with duplicated tokens...')
        previous_amount = len(self.df)
        self.delete_older_duplicates(False)
        new_amount = len(self.df)
        duplicates_deleted = previous_amount - new_amount
        self.deleted += duplicates_deleted
        self.out.l_info(f'Removed {duplicates_deleted} duplicates.')

        self.out.l_info('Validating responses...')

        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Delete responses with invalid tokens.
            if not self.is_valid(token) or not token:
                self.out.l_info(f'#{index} >> Invalid token')
                self._delete(index)
                continue

            self.out.l_verbose(f'#{index} >> OK')

        # Remove bad_token_column from dataframe.
        if self.bad_token_column:
            if not self.df[self.bad_token_column].empty:
                self.out.l_warning('bad_token_column is not empty. Dropping anyway...')
            self.df.drop([self.bad_token_column], axis=1)

        # Write data to csv file.
        self.df.to_csv(output_path, sep=',', index=False, encoding='utf-8')
        self.out.l_info(f'File saved as {output_path}.')

        # Pandas adds "Unnamed: ..." to columns without a name.
        # We have to remove that.
        self.out.l_info('Fixing headers...')
        Validator.fix_headers(output_path)

    def run_list(self):
        """
        The script will run in list mode. A list of responses to delete will be generated.
        """
        output_path = 'delete_' + self.file.name.split('.')[0] + '.txt'

        self.out.l_info('Fixing columns...')
        if self.bad_token_column:
            self.fix_token_position()

        # List responses with duplicated tokens.
        self.out.l_info('Checking responses with duplicated tokens...')
        duplicates = self.delete_older_duplicates(True)
        self.to_delete = self.df[duplicates][self.ID_FIELD].to_list()
        self.out.l_info(f'Found {len(self.to_delete)} duplicates.')

        self.out.l_info('Validating responses...')

        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Check responses with invalid tokens.
            if not self.is_valid(token) or not token:
                if token:
                    self.out.l_info(f'#{index} >> Invalid token')
                self.to_delete.append(self.df[self.ID_FIELD].iloc[index])
                continue

            self.out.l_verbose(f'#{index} >> OK')

        # Check bad_token_column.
        if self.bad_token_column and not self.df[self.bad_token_column].empty:
            self.out.l_warning('bad_token_column is not empty.')

        # Empty token fields are detected as duplicates and invalid tokens.
        # Remove the duplicates.
        clean_to_delete = [elem for index, elem in enumerate(self.to_delete) if elem not in self.to_delete[:index]]

        with open(output_path, 'w') as f:
            for elem in clean_to_delete:
                f.write(elem + '\n')
        self.out.l_info(f'File saved as {output_path}.')

        self.deleted = len(clean_to_delete)

    def is_valid(self, token: str) -> bool:
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

    def fix_token_position(self):
        """
        Fix tokens placed in an incorrect column.
        """
        for index, row in self.df.iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()
            if not token and len(row[self.bad_token_column]) == self.WCA_TOKEN_LEN:
                row[self.WCA_TOKEN_FIELD] = row[self.bad_token_column].strip()

    def _delete(self, index: int) -> None:
        """
        Delete dataframe row.
        """
        self.out.l_verbose(f'#{index} >> deleted')
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
