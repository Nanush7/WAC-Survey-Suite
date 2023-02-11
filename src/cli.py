"""
Copyright (c) 2022-2023 Nanush7. MIT license, see LICENSE file.
"""
import os.path
from random import randint
from src.modules import BaseModule

__version__ = '1.0'


class CLI:
    """
    Interactive CLI Class.
    """

    def __init__(self, file, output):
        self.out = output
        self.modules = []
        self.file = file
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

    def _get_modules(self):
        """
        Get modules.
        """
        modules = []
        for module in BaseModule.module_list:
            try:
                instance = module(self.file, self.out)
                self.out.p_green(f'[OK] <{module.name}> loaded.')
            except Exception:
                self.out.l_warning(
                    f'Could not import <{module.name}> module.')
            else:
                modules.append(instance)

        return modules

    def menu(self):
        # Print banner and options.
        self.out.clear()
        self.banner()
        print(f'''
Options:
    => 'd' to write the description of each module.
    => 'r' to reload modules.
    => 'exit' to shutdown each module and exit.
        ''')

        print('    File => ', end='')
        self.out.p_blue(self.file.name, end='\n\n')

        for i, module in enumerate(self.modules):
            print(f'>> [{i + 1}] {module.name}')

        print('\n\n\n')
        # TODO: Cerrar self.file al salir.
        # TODO: Avisar que close cierra aunque nunca se haya usado.

    def run(self):
        # Check if file was provided.
        if self.file is None:
            print('Please, provide the absolute or relative path to the survey CSV file.')
            self.file = input('File path: ')
            if not os.path.isfile(self.file):
                self.out.l_error('File not found.')
                exit(1)

        self.file = open(self.file, 'r')

        # Get modules.
        self.out.l_info('Loading modules...')
        self.modules = self._get_modules()

        # Run until exit.
        while True:
            print('Press enter to continue...')
            self.menu()
            break
        self.file.close()
