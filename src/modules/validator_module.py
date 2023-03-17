"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
import pandas
from os import path, makedirs
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
    VALIDATED_DIR = 'Validated'

    def __init__(self, **kwargs):
        # Add anything you want here.
        name = 'Validator'
        description = 'Validate tokens and remove duplicates.'
        version = '1.1'
        authors = 'Nanush7'
        super().__init__(name, description, version, authors, **kwargs)

        # Stats and other data.
        self.tokens_path = None
        self.token_list = []
        self.list_only = False
        self.total_responses = 0
        self.deleted = 0
        self.to_delete = []
        self.dataframes = {}
        self.bad_token_column = None

        # Menu.
        self.main_menu = builder.Menu(extra_start=f'\n{self.name} module v{self.version} by {self.authors}.\n',
                                      back_option=True)

    def startup(self):
        # Survey responses.
        # Load data as string to avoid Pandas adding floating points.

        # Pandas DataFrames.
        self.dataframes = Validator.get_dataframes(self.files)

        # Tokens.
        self.out.p_blue('Use Ctrl-C to abort setup.')
        try:
            while not self.tokens_path:
                t_path = input('Path to tokens file: ')
                if path.isfile(t_path):
                    self.tokens_path = t_path
                else:
                    self.out.p_yellow('File not found, try again.')
        except KeyboardInterrupt:
            return False

        with open(self.tokens_path, 'r', encoding='utf-8') as f:
            self.token_list = f.read().split('\n')

        # Build menu.
        self.main_menu.add_numbered_option('Delete invalid responses from original CSV file.')
        self.main_menu.add_numbered_option('List responses to delete.')

        # Create CSV output directory.
        if not path.exists(self.VALIDATED_DIR):
            makedirs(self.VALIDATED_DIR)

        return True

    @staticmethod
    def get_dataframes(files):
        """
        Get list of Pandas DataFrames for each file in self.file.
        """
        df = {}
        for file in files:
            df[file.name] = pandas.read_csv(file,
                                            encoding='utf-8',
                                            converters={i: str for i in range(Validator.MAX_COLUMNS)})

        return df

    def on_file_change(self, files):
        if self.startup_completed:
            self.dataframes = Validator.get_dataframes(files)

    def run(self) -> None:
        while True:
            choice = self.main_menu.display()
            if choice == 'back':
                break

            # Run option.
            if choice == '1':
                for survey in self.dataframes:
                    self.out.l_info(f'Validating {survey}...')
                    self.run_delete(survey)
                    self.out.l_info(f'Deleted {self.deleted} out of {self.total_responses} responses.')
            elif choice == '2':
                for survey in self.dataframes:
                    self.out.l_info(f'Validating {survey}...')
                    self.run_list(survey)
                    self.out.l_info(f'Deleted {self.deleted} out of {self.total_responses} responses.')

    def prepare_run(self, survey):
        # Reset some attributes on each run.
        self.total_responses = len(self.dataframes[survey]) - 1
        self.deleted = 0
        self.to_delete = []
        self.bad_token_column = self.dataframes[survey].columns[-1]
        if 'Unnamed' not in self.bad_token_column:
            self.bad_token_column = None
        else:
            self.out.l_warning('Bad Token Column found.')

    def run_delete(self, survey):
        """
        The script will run in deletion mode. A clean copy of the CSV file will be generated.
        """
        self.prepare_run(survey)

        output_path = f'{self.VALIDATED_DIR}/Validated_{survey.split("/")[-1]}'

        self.out.l_info('Fixing columns...')
        if self.bad_token_column:
            self.fix_token_position(survey)

        # Delete responses with duplicated tokens.
        self.out.l_info('Checking responses with duplicated tokens...')
        previous_amount = len(self.dataframes[survey])
        self.delete_older_duplicates(survey, False)
        new_amount = len(self.dataframes[survey])
        duplicates_deleted = previous_amount - new_amount
        self.deleted += duplicates_deleted
        self.out.l_info(f'Removed {duplicates_deleted} duplicates.')

        self.out.l_info('Validating responses...')

        for index, row in self.dataframes[survey].iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Delete responses with invalid tokens.
            if not self.is_valid(token) or not token:
                self.out.l_info(f'#{index} >> Invalid token')
                self._delete(survey, index)
                continue

            self.out.l_verbose(f'#{index} >> OK')

        # Remove bad_token_column from dataframe.
        if self.bad_token_column:
            if not self.dataframes[survey][self.bad_token_column].empty:
                self.out.l_warning('bad_token_column is not empty. Dropping anyway...')
            self.dataframes[survey].drop([self.bad_token_column], axis=1)

        # Write data to csv file.
        self.dataframes[survey].to_csv(output_path, sep=',', index=False, encoding='utf-8')
        self.out.l_info(f'File saved as {output_path}.')

        # Pandas adds "Unnamed: ..." to columns without a name.
        # We have to remove that.
        self.out.l_info('Fixing headers...')
        Validator.fix_headers(output_path)

    def run_list(self, survey):
        """
        The script will run in list mode. A list of responses to delete will be generated.
        """
        self.prepare_run(survey)

        output_path = f'{self.VALIDATED_DIR}/Delete_{survey.split("/")[-1]}.txt'

        self.out.l_info('Fixing columns...')
        if self.bad_token_column:
            self.fix_token_position(survey)

        # List responses with duplicated tokens.
        self.out.l_info('Checking responses with duplicated tokens...')
        duplicates = self.delete_older_duplicates(survey, True)
        self.to_delete = self.dataframes[survey][duplicates][self.ID_FIELD].to_list()
        self.out.l_info(f'Found {len(self.to_delete)} duplicates.')

        self.out.l_info('Validating responses...')

        for index, row in self.dataframes[survey].iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()

            # Check responses with invalid tokens.
            if not self.is_valid(token) or not token:
                if token:
                    self.out.l_info(f'#{index} >> Invalid token')
                self.to_delete.append(self.dataframes[survey][self.ID_FIELD].iloc[index])
                continue

            self.out.l_verbose(f'#{index} >> OK')

        # Check bad_token_column.
        if self.bad_token_column and not self.dataframes[survey][self.bad_token_column].empty:
            self.out.l_warning('bad_token_column is not empty.')

        # Empty token fields are detected as duplicates and invalid tokens.
        # Remove the duplicates.
        clean_to_delete = [elem for index, elem in enumerate(self.to_delete) if elem not in self.to_delete[:index]]

        with open(output_path, 'w', encoding='utf-8') as f:
            for elem in clean_to_delete:
                f.write(elem + '\n')
        self.out.l_info(f'File saved as {output_path}.')

        self.deleted = len(clean_to_delete)

    def is_valid(self, token: str) -> bool:
        """
        Check if the token is valid and delete the response if not.
        """
        return token in self.token_list

    def delete_older_duplicates(self, survey, list_only: bool = False):
        """
        Take the repeated tokens and delete (or list) all, except the newest one.

        :returns: DataFrame with the responses to delete or None if responses where deleted in place.
        pandas. Series | None
        """
        if list_only:
            duplicates = self.dataframes[survey].duplicated(subset=[self.WCA_TOKEN_FIELD], keep='first')
            return duplicates
        self.dataframes[survey].drop_duplicates(subset=[self.WCA_TOKEN_FIELD],
                                                keep='first', ignore_index=False, inplace=True)

    def fix_token_position(self, survey):
        """
        Fix tokens placed in an incorrect column.
        """
        for index, row in self.dataframes[survey].iloc[1:].iterrows():
            token = row[self.WCA_TOKEN_FIELD].strip()
            if not token and len(row[self.bad_token_column]) == self.WCA_TOKEN_LEN:
                row[self.WCA_TOKEN_FIELD] = row[self.bad_token_column].strip()

    def _delete(self, survey, index: int) -> None:
        """
        Delete dataframe row.
        """
        self.out.l_verbose(f'#{index} >> deleted')
        self.dataframes[survey].drop(index, axis=0, inplace=True)
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
