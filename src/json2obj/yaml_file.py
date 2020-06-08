#!/usr/bin/python3
"""
yaml_file.py
"""

from typing import Callable, Optional

import yaml

from .env_vars import check_for_env_vars
from .json2obj import JSON2Obj

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

class YamlFile:
    def __init__(self, file_path: str, env_var_function: Optional[Callable] = check_for_env_vars):
        """

        Args:
            file_path: Full path to file.
            env_var_function: Function to use for checking for env vars.
        """
        self.file_path = file_path
        self.yaml = YAML()
        self.env_var_function = env_var_function

    def load(self) -> JSON2Obj:
        data = self.read_file()
        return JSON2Obj(data, env_var_function=self.env_var_function)

    def read_file(self) -> CommentedMap:
        with open(self.file_path) as file:
            return self.yaml.load(file)

    def write_file(self, data: dict, rebase=True):
        if rebase:
            org_file = self.read_file()
            data.update(org_file)

        with open(self.file_path, 'w') as file:
            print(data)
            self.yaml.dump(data, file)
