"""
Copyright (c) 2022-2023 Nanush7. See LICENSE file.

Custom exceptions
"""


class ModuleError(Exception):
    def __init__(self, message):
        self.message = 'Module error: ' + message
