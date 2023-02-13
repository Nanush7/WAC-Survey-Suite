"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
import abc
import os
from importlib import util
from src.modules.exceptions import ModuleError


####################
# Module blueprint #
####################

class BaseModule(metaclass=abc.ABCMeta):
    """
    Base module class.
    """
    module_list = []

    def __init_subclass__(cls):
        """
        This is executed every time a subclass inherits from the base clase.
        """
        cls.module_list.append(cls)

    def __init__(self, name, description, **kwargs):
        self._name = name
        self._description = description
        self._file = kwargs['file']
        self.out = kwargs['output']

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def file(self):
        return self._file

    @abc.abstractmethod
    def run(self) -> None:
        """
        This method will be executed when the module is selected.
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        This method will be closed upon closing the cli.
        """
        pass


###################
# Interface utils #
###################

class Menu:
    """
    Create and display a menu.
    """
    def __init__(self, extra_start='', extra_end='', back_option=False):
        self._string_options = {}
        self.back_option = back_option
        self._numbered_options = []
        self.start = extra_start
        self.end = extra_end

    @staticmethod
    def _check_callable(obj) -> None:
        if obj is not None and not callable(obj):
            raise ModuleError("callback parameter must be a callable object.")

    def add_string_option(self, name, description, callback=None, *args, **kwargs) -> None:
        """
        These options will be displayed with the following format:
            => '{name}' to {description}.
        """
        Menu._check_callable(callback)
        self._string_options[name] = [description, callback, [args, kwargs]]

    def add_numbered_option(self, description, callback=None, *args, **kwargs) -> None:
        """
        These options will be displayed with the following format:
        >> [{option_number}] {description}.
        """
        Menu._check_callable(callback)
        self._numbered_options.append([description, callback, [args, kwargs]])

    def display(self):
        """
        Display menu and prompt for choice.
        """
        # Display.
        print(self.start, end='')
        print('Options:')
        for key, option in self._string_options.items():
            print(f'    => \'{key}\' to {option[0]}')
        if self.back_option:
            print('    => \'back\' to return to the previous menu.')

        print('')
        for index, option in enumerate(self._numbered_options):
            print(f'>> [{index + 1}] {option[0]}')
        print(self.end, end='')

        # Prompt until choice is valid.
        while True:
            choice = input('\n--> ')
            ret = None

            # Go back.
            if choice == 'back' and self.back_option:
                ret = 'back'
                break

            choice_is_decimal = choice.isdecimal()
            # The choice is a string.
            if not choice_is_decimal and choice in self._string_options.keys():
                callback = self._string_options[choice][1]
                if callback:
                    args = self._string_options[choice][2][0]
                    kwargs = self._string_options[choice][2][1]
                    ret = callback(*args, **kwargs)
                else:
                    ret = choice

            # The choice is a number.
            elif choice_is_decimal and int(choice) in range(1, len(self._numbered_options)+1):
                callback = self._numbered_options[int(choice) - 1][1]
                if callback:
                    args = self._numbered_options[int(choice) - 1][2][0]
                    kwargs = self._numbered_options[int(choice) - 1][2][1]
                    ret = callback(*args, **kwargs)
                else:
                    ret = choice

            # The choice is invalid.
            else:
                print('Invalid option. Try again.')
                continue

            # Break if choice was valid.
            break

        return ret

################
# Internal use #
################

def _load_module(path):
    name = os.path.split(path)[-1]
    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _init():
    path = os.path.abspath(__file__)
    dirpath = os.path.dirname(path)

    for file_name in os.listdir(dirpath):
        if file_name.endswith('_module.py'):
            _load_module(os.path.join(dirpath, file_name))
