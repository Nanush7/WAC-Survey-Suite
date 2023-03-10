"""
Compiler Module.
"""
import pandas
from re import search
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from src.modules import builder
from src.metadata import metadata


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
        self.questions_by_index = {}

        # Menus.
        self.main_menu = builder.Menu(extra_start=f'\nCompiler module v{self.version} by {self.authors}.\n',
                                      back_option=True)
        self.interests_menu = builder.Menu(back_option=True)
        self.additional_questions_menu = builder.Menu(back_option=True)

        # Tables.
        self.topics_table = builder.Table(['Code', 'Description'])

        # Jinja2 scheme template.
        self.jinja = Environment(loader=FileSystemLoader('src/metadata/'))

        # Pandas DataFrame.
        self.df = pandas.read_csv(self.file)

    def startup(self) -> bool:
        # Topics table.
        for code, description in self.topic_codes.items():
            self.topics_table.add_row([code, description])
        self.topics_table.align['Description'] = 'l'

        # Main menu setup.
        self.main_menu.add_numbered_option('Set topics by team/committee.', callback=self.set_interests)
        self.main_menu.add_numbered_option('Set additional questions by team/committee.',
                                           callback=self.set_additional_questions)
        self.main_menu.add_numbered_option('Generate scheme.', callback=self.generate_scheme_file)
        self.main_menu.add_string_option('compile', 'run compiler.', callback=self.compile)

        # Try to import scheme.
        try:
            from src.metadata import scheme
            self.team_topics = scheme.TEAM_INTERESTS
            self.team_columns = scheme.TEAM_COLUMNS
        except ImportError:
            # Disable the Compile option until scheme is generated.
            self.main_menu.disable_option(name='compile')

        # interests_menu setup.
        self.interests_menu.add_string_option('a', 'assign a topic')
        self.interests_menu.add_string_option('r', 'remove a topic')
        self.interests_menu.add_string_option('codes', 'display topic codes')
        self.interests_menu.add_string_option('list', 'display topics by team')

        # set_additional_questions menu.
        self.additional_questions_menu.add_string_option('a', 'add a question')
        self.additional_questions_menu.add_string_option('r', 'remove a question')
        self.additional_questions_menu.add_string_option('questions', 'show all questions by index.')

        # Drop unwanted columns.
        for column in self.df.columns:
            if column in self.must_delete_columns:
                self.df.drop(column, axis=1)

        # Get all questions.
        for index, column in enumerate(self.df.columns):
            if metadata.PANDAS_UNNAMED not in column and metadata.SEPARATOR_QUESTION not in column:
                self.questions_by_index[index] = column

        return True

    def _get_interests_table(self):
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

    def _print_questions(self):
        """
        Questions by topic.
        """


    def _get_topic_columns(self) -> dict[str, list[int]]:
        code_columns = {}
        start = 0
        code = '0'  # Start with "General Questions" code.
        for index, column_label in enumerate(self.df.columns):
            match = search(r'^\d+\)', column_label)  # Search for "number)".
            if match:
                end = index
                code_columns[code] = [*range(start, end)]  # * unpacks the range to a list.
                code = match.group()[:-1]  # [:-1] removes the parenthesis from the matched code.
                start = index
        # Edge case: last code does not end by finding another code.
        code_columns[code] = [*range(start, start+1)]  # Should be only one column: "Other comments".

        return code_columns

    def _generate_team_columns(self) -> None:
        self.team_columns = {}
        # Get columns for each topic.
        self.topic_columns = self._get_topic_columns()

        # Assign columns to teams based on topics.
        for team in self.teams.keys():
            self.team_columns[team] = []
            for code, columns in self.topic_columns.items():
                if code in self.team_topics[team]:
                    self.team_columns[team].extend(columns)

    def generate_scheme_file(self):
        template = self.jinja.get_template('scheme.py.jinja')

        self._generate_team_columns()

        scheme = template.render(date=datetime.now(),
                                 version=self.version,
                                 teams=self.team_topics,
                                 topics=self.topic_columns,
                                 team_columns=self.team_columns)

        with open('src/metadata/scheme.py', 'w') as f:
            f.write(scheme)
        self.out.p_green('scheme.py generated successfully.')
        self.main_menu.enable_option(name='compile')

    def compile(self):
        pass

    def set_additional_questions(self):
        # Update team columns with current selected topics.
        while True:
            # Display menu and prompt for choice.
            choice = self.additional_questions_menu.display()
            if choice == 'questions':
                self._print_questions()
            elif choice == 'back':
                break
            else:
                team = input('Initials of the team/committee to edit: ').upper()
                selected_questions = input(
                    'Indexes of the questions to add/remove separated with commas: ').replace(' ', '').split(',')

                # Check team.
                if team not in self.teams.keys():
                    self.out.l_error('Team not found.')
                    return 'error'

                for question_index in selected_questions:
                    if question_index not in self.questions_by_index.keys():  # Check topic.
                        self.out.l_error(f'Invalid index: {question_index}')
                        return 'error'

                    if choice == 'a' and question_index not in self.team_columns[team]:  # Add.
                        self.team_topics[team].append(question_index)
                    elif choice == 'r' and question_index in self.team_columns[team]:  # Remove.
                        self.team_topics[team].remove(question_index)

                # Update team columns.
                # TODO: Hacer que el compilador busque el rango de cada pregunta solo: no añadir todas las columnas para cada equipo.
                self.out.p_green('Done.')

    def set_interests(self):
        print(self._get_interests_table())
        while True:
            # Display menu and prompt for choice.
            choice = self.interests_menu.display()
            if choice == 'list':
                print(self._get_interests_table())
            elif choice == 'codes':
                print(self.topics_table)
            elif choice == 'back':
                break
            else:
                team = input('Initials of the team/committee to edit: ').upper()
                selected_codes = input(
                    'Code of the topics to add/remove separated with commas: ').replace(' ', '').split(',')

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

    def on_file_change(self, file):
        self.df = pandas.read_csv(file)

    def run(self):
        while self.main_menu.display() != 'back':
            input('\nPress enter to continue...')
            self.out.clear()
