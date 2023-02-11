import abc
import os
from importlib import util


class BaseModule(metaclass=abc.ABCMeta):
    """
    Base module class.
    """
    module_list = []
    name: str = 'Base Module'  # Default.
    description: str = 'No description.'

    def __init_subclass__(cls):
        """
        This is executed every time a subclass inherits from the base clase.
        """
        cls.module_list.append(cls)

    def __init__(self, client, logger):
        self.client = client
        self.logger = logger

    def close(self) -> None:
        """
        This method will be closed upon closing the cli.
        """
        pass

    @abc.abstractmethod
    def run(self) -> None:
        """
        This method will be executed when the module is selected.
        """
        raise NotImplementedError


# Load modules.
def load_module(path):
    name = os.path.split(path)[-1]
    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


path = os.path.abspath(__file__)
dirpath = os.path.dirname(path)

for file_name in os.listdir(dirpath):
    if file_name.endswith('_module.py'):
        load_module(os.path.join(dirpath, file_name))
