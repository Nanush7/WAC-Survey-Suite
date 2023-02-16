#  Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
Compiler Module.
"""
from jinja2 import Environment, DictLoader
from src.modules import builder
from src.metadata import metadata


class Compiler(builder.BaseModule):
    """
    Compiler class.
    """
    def __init__(self, **kwargs):
        name = 'Compiler'
        description = 'Compile the relevant data for each committee/team.'
        version = '1.0'
        authors = 'AnnikaStein, Nanush7'
        self.teams = metadata.TEAMS
        self.topic_codes = metadata.TOPIC_CODES
        self.team_topics = metadata.TEAM_DEFAULT_INTEREST
        self.scheme = None
        self.interests_menu = builder.Menu(back_option=True)
        self.topics_table = builder.Table(['Code', 'Description'])
        self.jinja = Environment()  # TODO: Terminar acá.
        super().__init__(name, description, version, authors, **kwargs)

    def get_interests_table(self):
        interests_table = builder.Table(['Team/Committee', 'Topics'])
        for key, team in self.teams.items():
            topics = ''
            for topic in self.team_topics[key]:
                topics += self.topic_codes[topic] + ', '
            interests_table.add_row([team, topics])
        interests_table.align = 'l'
        return interests_table

    def generate_scheme_file(self):
        pass

    def compile(self):
        pass

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

    def run(self):
        # Main menu.
        main_menu = builder.Menu(extra_start=f'\nCompiler module v{self.version} by {self.authors}.\n', back_option=True)
        main_menu.add_numbered_option('Set topics by team/committee.', callback=self.set_interests)
        main_menu.add_numbered_option('Generate scheme.', callback=self.generate_scheme_file)
        main_menu.add_numbered_option('Compile data.', callback=self.compile)
        try:
            from src.metadata import scheme
        except ImportError:
            # Disable the Compile option until scheme is generated.
            # Change index below if you add or change options.
            main_menu.disable_option(index=3)

        for code, description in self.topic_codes.items():
            self.topics_table.add_row([code, description])
        self.topics_table.align['Description'] = 'l'

        # set_interests menu.
        self.interests_menu.add_string_option('a', 'assign a topic')
        self.interests_menu.add_string_option('r', 'remove a topic')
        self.interests_menu.add_string_option('codes', 'display topic codes')
        self.interests_menu.add_string_option('list', 'display the list again')

        while main_menu.display() != 'back':
            input('\nPress enter to continue...')
