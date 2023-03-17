"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
from os import path, listdir
from random import randint
from src.modules import builder

__version__ = '1.1.1'


class CLI:
    """
    Interactive CLI Class.
    """

    def __init__(self, directory, output):
        self.out = output
        self.modules = []
        self.files = []
        self._file_manager(directory)  # Open CSV files and save them to self.files.
        self.main_menu = builder.Menu()
        self.mod_descriptions = []
        # Banner use only.
        self.colors = [self.out.p_blue, self.out.p_yellow, self.out.p_red, self.out.p_green]

    def banner(self):
        # Use a random color each time.
        color_func = self.colors[randint(0, 3)]
        color_func(f'''
██╗    ██╗ █████╗  ██████╗    ███████╗      ███████╗██╗   ██╗██╗████████╗███████╗
██║    ██║██╔══██╗██╔════╝    ██╔════╝      ██╔════╝██║   ██║██║╚══██╔══╝██╔════╝
██║ █╗ ██║███████║██║         ███████╗█████╗███████╗██║   ██║██║   ██║   █████╗  
██║███╗██║██╔══██║██║         ╚════██║╚════╝╚════██║██║   ██║██║   ██║   ██╔══╝  
╚███╔███╔╝██║  ██║╚██████╗    ███████║      ███████║╚██████╔╝██║   ██║   ███████╗
 ╚══╝╚══╝ ╚═╝  ╚═╝ ╚═════╝    ╚══════╝      ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝ 
                                                                            v{__version__}
''')

    def _load_modules(self):
        """
        Load modules.
        """
        self.modules = []
        self.main_menu.remove_numbered_all()
        builder._init()
        for module in builder.BaseModule.module_list:
            try:
                instance = module(files=self.files, output=self.out)
                self.out.p_green(f'[OK] {instance.name} loaded.')
            except Exception as exc:
                self.out.l_warning(
                    f'Could not import {module} ({exc})')
            else:
                self.modules.append(instance)
                self.main_menu.add_numbered_option(instance.name)

    def _file_manager(self, directory=None):
        """
        Open file, save it to self.file and change it in all modules.
        """
        if not directory:  # Ask for dir path.
            print('Please, provide the absolute or relative path to the directory containing the CSV files.')
            directory = input('Directory path: ')

        if not path.isdir(directory):  # Fail if not found.
            self.out.l_error('Directory not found.')
            return

        for file in self.files:  # Close files if already opened.
            try:
                file.close()
            except AttributeError:
                pass

        self.files = []
        for filename in listdir(directory):
            if filename.endswith('.csv'):
                self.files.append(open(f'{directory}/{filename}', 'r', encoding='utf-8'))
        for module in self.modules:
            module.files = self.files

    def menu(self) -> bool:
        # Print banner and options.
        self.out.clear()
        self.banner()

        # Display active filenames.
        print('    Files => ', end='')
        self.out.p_blue(self.files[0].name, end='')
        for file in self.files[1:]:
            self.out.p_blue(f', {file.name}', end='')
        print('\n')

        choice = self.main_menu.display()

        if choice == 'exit':
            for m in self.modules:
                if m.startup_completed:
                    m.close()
            return False  # False kills the main loop.
        elif choice == 'd':
            if not self.mod_descriptions:
                self.mod_descriptions = builder.Table(
                    ['Name', 'Description', 'Version', 'Author(s)'],
                    [[m.name, m.description, m.version, m.authors] for m in self.modules]
                )
            print(self.mod_descriptions)

        elif choice == 'r':
            self.out.l_info('Reloading modules...')
            self._load_modules()
        elif choice:
            self.out.clear()
            module = self.modules[int(choice) - 1]
            # Don't run module if setup fails.
            if not module.startup_completed and module.startup():  # startup returns True if successful.
                module.startup_completed = True
            if module.startup_completed:
                self.out.clear()
                module.run()
            else:
                self.out.l_error('Startup failed.')
        elif choice is not None:
            # Some callback returned something, but it was not caught.
            self.out.l_warning('Please, report this message to the developer.')

        return True

    def run(self):
        # LICENSE notice.
        print('''
    WAC Survey Suite Copyright (C) 2023 Nanush7
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions. See LICENSE file for more details.
''')

        while len(self.files) == 0:
            self._file_manager()

        self.main_menu.add_string_option('c', 'change the current directory.', self._file_manager)
        self.main_menu.add_string_option('d', 'write the description of each module')
        self.main_menu.add_string_option('r', 'reload modules')
        self.main_menu.add_string_option('exit', 'close modules and exit')

        # Get modules.
        self.out.l_info('Loading modules...')
        self._load_modules()
        input('\nPress enter to continue...')

        # Run until exit.
        try:
            while self.menu():
                input('\nPress enter to continue...')
        except KeyboardInterrupt:
            print('\nKeyboard interrupt caught! Closing...')
        finally:
            for file in self.files:
                try:
                    file.close()
                except AttributeError:
                    pass
