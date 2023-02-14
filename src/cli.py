"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
import os.path
from random import randint
from src.modules import builder

__version__ = '1.0'


class CLI:
    """
    Interactive CLI Class.
    """

    def __init__(self, file, output):
        self.out = output
        self.modules = []
        self.file = file
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
                instance = module(file=self.file, output=self.out)
                self.out.p_green(f'[OK] {instance.name} loaded.')
            except Exception as exc:
                self.out.l_warning(
                    f'Could not import {module} ({exc})')
            else:
                self.modules.append(instance)
                self.main_menu.add_numbered_option(instance.name)

    def menu(self) -> bool:
        # Print banner and options.
        self.out.clear()
        self.banner()

        print('    File => ', end='')
        self.out.p_blue(self.file.name, end='\n\n')

        choice = self.main_menu.display()

        if choice == 'exit':
            return False
        elif choice == 'd':
            if not self.mod_descriptions:
                self.mod_descriptions = builder.Table(
                    ['Name', 'Description', 'Version'],
                    [[m.name, m.description, m.version] for m in self.modules]
                )
            print(self.mod_descriptions)

        elif choice == 'r':
            self.out.l_info('Reloading modules...')
            self._load_modules()
        else:
            self.modules[int(choice) - 1].run()

        return True

    def run(self):
        # LICENSE notice.
        print('''
    WAC Survey Suite Copyright (C) 2023 Nanush7
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions. See LICENSE file for more details.
''')

        # Check if file was provided.
        if self.file is None:
            print('Please, provide the absolute or relative path to the survey CSV file.')
            self.file = input('File path: ')
            if not os.path.isfile(self.file):
                self.out.l_error('File not found.')
                exit(1)

        self.file = open(self.file, 'r')

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
                input('Press enter to continue...')
        except KeyboardInterrupt:
            print('\nKeyboard interrupt caught! Closing...')
        finally:
            # If the file was not opened, it shouldn't reach this line anyway.
            self.file.close()
