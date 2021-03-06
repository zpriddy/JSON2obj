#!/usr/bin/python3
"""
yaml_file.py
"""

from typing import Callable, Optional

import json

from .env_vars import check_for_env_vars
from .json2obj import JSON2Obj


class JsonFile:
    def __init__(self, file_path: str, env_var_function: Optional[Callable] = check_for_env_vars):
        """

        Args:
            file_path: Full path to file.
            env_var_function: Function to use for checking for env vars.
        """
        self.file_path = file_path
        self.env_var_function = env_var_function


    def load(self) -> JSON2Obj:
        data = self.read_file()
        return JSON2Obj(data, env_var_function=self.env_var_function)


    def read_file(self) -> dict:
        with open(self.file_path) as file:
            return json.load(file)

    def write_file(self, data: dict, rebase=True):
        if rebase:
            org_file = self.read_file()
            data.update(org_file)

        with open(self.file_path, 'w') as file:
            json.dump(data, file)
