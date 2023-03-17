"""
Compiler Module.
"""
import pandas
from re import search, sub
from os import path, makedirs
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from src.modules import builder, exceptions
from src.metadata import metadata


COMPILED_DIR = 'Compiled'


class Compiler(builder.BaseModule):
    """
    Compiler class.
    """
    def __init__(self, **kwargs):
        name = 'Compiler'
        description = 'Compile the relevant data for each committee/team.'
        version = '2.0'
        authors = 'AnnikaStein, Nanush7'

        super().__init__(name, description, version, authors, **kwargs)

        # Metadata.
        self.teams = metadata.TEAMS
        self.topic_codes = metadata.TOPIC_CODES
        self.team_topics = metadata.TEAM_DEFAULT_INTEREST
        self.team_columns = {}
        self.must_delete_columns = metadata.MUST_DELETE_COLUMNS
        self.questions_by_survey = {}
        self.dataframes = {}

        # Menus.
        self.main_menu = builder.Menu(extra_start=f'\nCompiler module v{self.version} by {self.authors}.\n',
                                      back_option=True)
        self.interests_menu = builder.Menu(back_option=True)

        # Tables.
        self.topics_table = builder.Table(['Code', 'Description'])

        # Jinja2 scheme template.
        self.jinja = Environment(loader=FileSystemLoader('src/metadata/'))

    def startup(self) -> bool:
        # Pandas DataFrames.
        self.dataframes = Compiler.get_dataframes(self.files)

        # Topics table.
        for code, description in self.topic_codes.items():
            self.topics_table.add_row([code, description])
        self.topics_table.align['Description'] = 'l'

        # Main menu setup.
        self.main_menu.add_numbered_option('Set topics by team/committee.', callback=self.set_interests)
        self.main_menu.add_numbered_option('Generate scheme.', callback=self.generate_scheme_file)
        self.main_menu.add_string_option('compile', 'compile questions for a team/committee.', callback=self.compile)

        # Try to import scheme.
        try:
            from src.metadata import scheme
            self.team_topics = scheme.TEAM_INTERESTS
            self.questions_by_survey = scheme.SURVEYS
        except ImportError:
            pass

        # interests_menu setup.
        self.interests_menu.add_string_option('a', 'assign a topic.')
        self.interests_menu.add_string_option('r', 'remove a topic.')
        self.interests_menu.add_string_option('codes', 'display topic codes.')
        self.interests_menu.add_string_option('list', 'display topics by team.')

        # Drop unwanted columns.
        self.out.l_info('Dropping unwanted columns...')
        for survey in self.dataframes.values():
            for column_label in self.must_delete_columns:
                try:
                    survey.drop(column_label, axis=1, inplace=True)
                except KeyError:
                    self.out.l_warning(f'{column_label} not found. Skipped.')

        # Get questions by topic for each survey.
        if not self.questions_by_survey:
            for name, survey in self.dataframes.items():
                self.questions_by_survey[name] = self.get_topic_questions(survey)

        # Create CSV output directory.
        if not path.exists(COMPILED_DIR):
            makedirs(COMPILED_DIR)

        return True

    @staticmethod
    def get_dataframes(files):
        df = {}
        for file in files:
            df[file.name] = pandas.read_csv(file, encoding='utf-8')

        return df

    def get_topic_questions(self, survey):
        """
        Get questions by topic.
        :returns: dict[str, list[str]]
        """
        questions = {}
        topic = '0'
        for code in self.topic_codes.keys():
            questions[code] = []
        for index, column_label in enumerate(survey.columns):
            match = search(r'^\d+\)', column_label)  # Search for "number)".
            if match and match.group()[:-1] == '6':  # TODO: Abstract "Other Comments" code. Edge case.
                topic = '6'
                questions[topic].append(column_label)
            elif match:
                topic = match.group()[:-1]  # [:-1] removes the parenthesis from the matched code.
            elif metadata.PANDAS_UNNAMED not in column_label:
                questions[topic].append(column_label)

        return questions

    def get_question_range(self, survey, question: str):
        """
        Get question column range.
        :returns: tuple[int, int]
        """
        start = None
        end = None
        columns = survey.columns
        for index, column_label in enumerate(columns):
            if column_label == question:
                start = index
                end = start + 1
                while end < len(columns) and metadata.PANDAS_UNNAMED in columns[end]:
                    end += 1
                break

        if start is None or end is None:
            self.out.l_error('Critical error.')
            raise exceptions.ModuleError('Critical error trying to locate question. Please, open an issue.')

        return start, end

    def get_interests_table(self):
        """
        Topics by team.
        """
        interests_table = builder.Table(['Team/Committee', 'Topics'])
        for key, team in self.teams.items():
            topics = ''
            for topic in self.team_topics[key]:
                topics += self.topic_codes[topic] + ', '
            interests_table.add_row([team, topics])
        interests_table.align = 'l'
        return interests_table

    def print_questions(self):
        """
        Questions by topic.
        """
        for topic, questions in self.questions_by_survey.items():
            print(f'----{metadata.TOPIC_CODES[topic]}----')
            for index, question in enumerate(questions):
                print(f'{index} > {question}')

    def generate_scheme_file(self):
        template = self.jinja.get_template('scheme.py.jinja')

        scheme = template.render(date=datetime.now(),
                                 version=self.version,
                                 teams=self.team_topics,
                                 surveys=self.questions_by_survey)

        with open('src/metadata/scheme.py', 'w', encoding='utf-8') as f:
            f.write(scheme)
        self.out.p_green('scheme.py generated successfully.')

    def get_additional_questions(self, survey: str, team: str):
        """
        Get questions selected manually.
        :returns: list[str]
        """
        additional_questions = []
        available_questions = []
        self.out.p_blue('\nAdditional questions available:')
        for topic, questions in self.questions_by_survey[survey].items():
            # Ignore questions from an already selected topic.
            if topic in self.team_topics[team] or len(questions) == 0:
                continue

            # Display available questions for current topic.
            self.out.p_yellow(f'\n<<< {self.topic_codes[topic]} >>>\n')
            for question in questions:
                print(f'[{len(available_questions)+1}] {question}')
                available_questions.append(question)

        selected_questions = input('\nQuestions to add, separated by commas: ').replace(' ', '').split(',')

        for num in selected_questions:
            try:
                index = int(num)
            except ValueError:
                self.out.l_error(f'Invalid input.')
                return []

            if index <= 0 or index > len(available_questions):
                self.out.l_error(f'Invalid index: {index}')
                return []

            additional_questions.append(available_questions[index-1])

        return additional_questions

    def compile(self):
        # Show teams.
        print('Teams/committees available:')
        for team in self.teams.keys():
            print(f'- {team}')

        # Select a team.
        team = input('\nSelect a team to compile: ')
        if team not in self.teams.keys():
            self.out.l_error('Team not found.')
            return 'error'

        # The procedure will be done for each survey.
        for title, survey in self.dataframes.items():

            self.out.p_green(f'\nSummary for {title}\n')
            self.out.p_blue('Questions to compile (based on selected topics):\n')
            team_questions = []
            for topic in self.team_topics[team]:
                for question in self.questions_by_survey[title][topic]:
                    team_questions.append(question)
                    print(f'- {question}')

            additional_questions = []
            while True:
                # Display additional questions.
                if len(additional_questions) != 0:
                    self.out.p_blue(f'\nAdditional questions to compile ({title}):\n')
                    for question in additional_questions:
                        print(f'- {question}')

                if builder.query_yes_no('\nDo you want to add additional questions?', default='no'):
                    additional_questions.extend(self.get_additional_questions(title, team))
                else:
                    break

            all_questions = additional_questions + team_questions

            # Compile.
            self.out.clear()
            self.out.l_info(f'Compiling {len(all_questions)} questions...')
            question_indexes = []
            for question in all_questions:
                question_range = self.get_question_range(survey, question)
                question_indexes.extend([*range(question_range[0], question_range[1])])

            compiled_df = survey.iloc[:, question_indexes]

            # Save to file.
            filename = f'{team}_{title.split("/")[-1]}'
            compiled_df.to_csv(f'{COMPILED_DIR}/{filename}', sep=',', index=False, encoding='utf-8')

            # Remove "Unnamed: ..." from column headers.
            with open(f'{COMPILED_DIR}/{filename}', 'r', encoding='utf-8') as f:
                content = f.read()

            content = sub(r'(Unnamed: )[0-9]+', '', content)

            # Write fixed content.
            with open(f'{COMPILED_DIR}/{filename}', 'w', encoding='utf-8') as f:
                f.write(content)

            self.out.l_info(f'Compiled CSV saved to {COMPILED_DIR}/{filename}.')

            # Generate report.
            template = self.jinja.get_template('report.txt.jinja')

            report = template.render(date=datetime.now(),
                                     version=self.version,
                                     team=team,
                                     title=title,
                                     filename=filename,
                                     total_responses=len(survey)-1,
                                     team_questions=team_questions,
                                     additional_questions=additional_questions)

            with open(f'{COMPILED_DIR}/report_{team}.txt', 'a', encoding='utf-8') as f:
                f.write(report)
            self.out.l_info(f'Report saved to {COMPILED_DIR}/report_{team}.txt')
            self.out.p_green(f'{title} compiled successfully!')

        self.out.p_green('All surveys compiled successfully!')

    def set_interests(self):
        print(self.get_interests_table())
        while True:
            # Display menu and prompt for choice.
            choice = self.interests_menu.display()
            if choice == 'list':
                print(self.get_interests_table())
            elif choice == 'codes':
                print(self.topics_table)
            elif choice == 'back':
                break
            else:
                team = input('Initials of the team/committee to edit: ').upper()
                selected_codes = input(
                    'Code of the topics to add/remove separated by commas: ').replace(' ', '').split(',')

                # Check team.
                if team not in self.teams.keys():
                    self.out.l_error('Team not found.')
                    return 'error'

                for topic in selected_codes:
                    if topic not in self.topic_codes.keys():  # Check topic.
                        self.out.l_error('Topic not found.')
                        return 'error'

                    if choice == 'a' and topic not in self.team_topics[team]:  # Add.
                        self.team_topics[team].append(topic)
                    elif choice == 'r' and topic in self.team_topics[team]:  # Remove.
                        self.team_topics[team].remove(topic)

                self.out.p_green('Done.')

    def on_file_change(self, files):
        if self.startup_completed:
            self.dataframes = Compiler.get_dataframes(files)

    def run(self):
        while self.main_menu.display() != 'back':
            input('\nPress enter to continue...')
            self.out.clear()
