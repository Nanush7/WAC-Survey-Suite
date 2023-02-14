"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.
"""
from src.modules.builder import BaseModule


class Validator(BaseModule):

    def __init__(self, **kwargs):
        # Add anything you want here.
        name = "Validator"
        description = "Validate tokens and remove duplicates."
        version = '1.0'
        super().__init__(name, description, version, **kwargs)

    def run(self) -> None:
        print("Hello World! :D")

    def close(self) -> None:
        print("Closing " + self.name)
