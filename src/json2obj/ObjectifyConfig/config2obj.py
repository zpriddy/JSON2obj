#!/usr/bin/python3
"""
config2obj.py	
"""
from ..json2obj import JSON2Obj
from ..env_vars import check_for_env_vars
from ..json_file import JsonFile
from ..yaml_file import YamlFile
from typing import Optional, Callable
from pathlib import Path


class Config2Obj:
    def __init__(
        self, user_config: str, config_template: str, env_var_function: Optional[Callable] = check_for_env_vars
    ):

        self.__env_var_function = env_var_function

        self.__user_path = user_config
        self.__template_path = config_template

        file_type = self.check_files(user_config, config_template)
        if file_type == "yaml":
            self.__user_config = YamlFile(user_config, env_var_function).load()
            self.__config_template = YamlFile(config_template, env_var_function).load()
        else:
            self.__user_config = JsonFile(user_config, env_var_function).load()
            self.__config_template = JsonFile(config_template, env_var_function).load()

    def update_user_config_from_template(self, update: bool = True, save: bool = False):
        user_config_dict = JSON2Obj.to_dict(self.__user_config)
        config_template_dict = JSON2Obj.to_dict(self.__config_template)
        config_template_dict.update(user_config_dict)
        if update:
            self.__user_config = JSON2Obj(config_template_dict)

        if save:

            # TODO: Update the user config object
            # TODO: Update user config file?
            pass



    @staticmethod
    def get_file_type(file_path: str) -> str:
        path = Path(file_path)
        if path.suffix.lower() not in [".yaml", ".json"]:
            raise TypeError("files are not yaml or json")
        return path.suffix.lower()[1:]

    @staticmethod
    def check_files(file_1: str, file_2: str) -> str:
        type_1 = Config2Obj.get_file_type(file_1)
        type_2 = Config2Obj.get_file_type(file_2)
        if type_1 != type_2:
            raise TypeError(f"{file_1} file type does not match {file_2}")
        return type_1

    @staticmethod
    def read_raw_file(file_path: str) -> dict:
        file_type = Config2Obj.get_file_type(file_path)
        if file_type == "json":
            return JsonFile(file_path).read_file()
        if file_type == "yaml":
            return YamlFile(file_path).read_file()
        raise TypeError(f"unknown file type: {file_path}")
