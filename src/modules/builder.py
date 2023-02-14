"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
import abc
import os
from importlib import util
from prettytable import PrettyTable
from src.modules.exceptions import ModuleError


####################
# Module blueprint #
# (abstract class) #
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

    def __init__(self, name, description, version, **kwargs):
        self._name = name
        self._description = description
        self._version = version
        self._file = kwargs['file']
        self.out = kwargs['output']

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def version(self):
        return self._version

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
        self._numbered_options = {}
        self.start = extra_start
        self.end = extra_end

    @staticmethod
    def _check_callable(obj) -> None:
        if obj is not None and not callable(obj):
            raise ModuleError("callback parameter must be a callable object.")

    def _check_name(self, name=None, index=None):
        """
        Check if name or index exists.
        """
        if name and name not in self._string_options:
            raise ModuleError('Cannot remove option, name does not exist.')
        if index and index not in self._numbered_options:
            raise ModuleError('Cannot remove option, index out of range')

    def add_string_option(self, name, description, callback=None, *args, **kwargs) -> None:
        """
        These options will be displayed with the following format:
            => '{name}' to {description}.
        """
        Menu._check_callable(callback)
        self._string_options[name] = [description, True, callback, [args, kwargs]]

    def add_numbered_option(self, description, callback=None, *args, **kwargs) -> None:
        """
        These options will be displayed with the following format:
        >> [{option_number}] {description}.
        """
        Menu._check_callable(callback)
        self._numbered_options[len(self._numbered_options)+1] = [description, True, callback, [args, kwargs]]

    def remove_string_option(self, name: str):
        """
        Remove menu option with the provided name.
        """
        if not isinstance(name, str) or name not in self._string_options:
            raise ModuleError('Cannot remove option, invalid name.')
        del self._string_options[name]

    def remove_numbered_option(self, index: int):
        """
        Remove menu option with the given index (note that index starts at 1).
        """
        if not isinstance(index, int) or index not in self._numbered_options:
            raise ModuleError('Cannot remove option, invalid index')
        del self._numbered_options[index]

    def remove_numbered_all(self):
        """
        Remove all numbered options.
        """
        self._numbered_options = {}

    def remove_string_all(self):
        """
        Remove all string options.
        """
        self._string_options = {}

    def enable_option(self, name=None, index=None):
        """
        Enable a previously disabled menu option.
        Raises: ModuleError if name or index is invalid.
        """
        if name:
            self._check_name(name=name)
            self._string_options[name][1] = True
        elif index:
            self._check_name(index=index)
            self._numbered_options[index][1] = True

    def disable_option(self, name=None, index=None) -> None:
        """
        Disable menu option, this will cause the option to print a message and prompt for choice again.
        Raises: ModuleError if name or index is invalid.
        """
        if name:
            self._check_name(name=name)
            self._string_options[name][1] = False
        elif index:
            self._check_name(index=index)
            self._numbered_options[index][1] = False

    def display(self):
        """
        Display menu and prompt for choice.
        """
        # Display.
        print(self.start, end='')
        print('Options:')
        for key, option in self._string_options.items():
            # Check if option is enabled.
            if option[1]:
                c = '>'
            else:
                c = 'X'
            print(f'    ={c} \'{key}\' to {option[0]}')
        if self.back_option:
            print('    => \'back\' to return to the previous menu.')

        print('')
        for index, option in self._numbered_options.items():
            if option[1]:
                c = '>'
            else:
                c = 'X'
            print(f'>{c} [{index}] {option[0]}')
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
                option = self._string_options[choice]

            # The choice is a number.
            elif choice_is_decimal and int(choice) in self._numbered_options:
                option = self._numbered_options[int(choice)]

            # The choice is invalid.
            else:
                print('Invalid option. Try again.')
                continue

            # Do something with the option.
            if not option[1]:
                print('Option disabled. Try again.')
                continue
            callback = option[2]
            if callback:
                args = option[3][0]
                kwargs = option[3][1]
                ret = callback(*args, **kwargs)
            else:
                ret = choice

            # Break if choice was valid.
            break

        return ret


class Table(PrettyTable):
    """
    Generate ASCII tables.
    This class is a PrettyTable wrapper.
    """
    def __init__(self, fields: list, rows=()):
        """
        fields: A list of columns to add to the table.
        rows: A list of lists.
        """
        super().__init__()
        self.field_names = fields
        if rows:
            for row in rows:
                self.add_row(row)

    def add_row(self, row: list):
        """
        Validate before calling parent method.
        """
        difference = len(self.field_names) - len(row)
        if difference > 0:
            empty_spaces = [''] * difference
            row.extend(empty_spaces)
        elif difference < 0:
            raise ModuleError(f'Too many values given to table row ({abs(difference)} more than expected).')
        super().add_row(row)


def query_yes_no(question, default=None) -> bool:
    """
    Ask a yes/no question via input() and return the answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes", "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {'yes': True, 'y': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ModuleError(f'Invalid default answer "{default}"')

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print('Invalid answer. Try again.')


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
    BaseModule.module_list = []
    path = os.path.abspath(__file__)
    dirpath = os.path.dirname(path)

    for file_name in os.listdir(dirpath):
        if file_name.endswith('_module.py'):
            _load_module(os.path.join(dirpath, file_name))
