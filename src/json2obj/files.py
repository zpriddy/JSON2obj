#!/usr/bin/python3
"""
files.py	
"""
from pathlib import Path
from .json_file import JsonFile
from .yaml_file import YamlFile
from .json2obj import JSON2Obj
from .env_vars import check_for_env_vars
from typing import Union, Callable, Optional
from ruamel.yaml.comments import CommentedMap
from enum import Enum


class FileTypes(str, Enum):
    JSON = "json"
    YAML = "yaml"


def get_file_type(file_path: str) -> FileTypes:
    path = Path(file_path)
    try:
        return FileTypes(path.suffix.lower()[1:])
    except ValueError:
        raise TypeError("files are not yaml or json")


def write_object_to_file(
    data: JSON2Obj, file_path: str, rebase: bool = True, env_var_function: Optional[Callable] = check_for_env_vars
):
    data_dict = JSON2Obj.to_dict(data)
    write_dict_to_file(data=data_dict, file_path=file_path, rebase=rebase, env_var_function=env_var_function)


def write_dict_to_file(
    data: dict, file_path: str, rebase: bool = True, env_var_function: Optional[Callable] = check_for_env_vars
):
    file_type = get_file_type(file_path)
    if file_type == FileTypes.JSON:
        JsonFile(file_path, env_var_function).write_file(data, rebase=rebase)
    elif file_type == FileTypes.YAML:
        YamlFile(file_path, env_var_function).write_file(data, rebase=rebase)
    else:
        raise TypeError(f"unknown file type: {file_path}")


# TODO: Missing env_var_function?
def get_file_objects(file_path: str) -> Union[JsonFile, YamlFile]:
    file_type = get_file_type(file_path)
    if file_type == FileTypes.JSON:
        return JsonFile(file_path)
    if file_type == FileTypes.YAML:
        return YamlFile(file_path)
    raise TypeError(f"unknown file type: {file_path}")


def read_raw_file(file_path: str) -> Union[dict, CommentedMap]:
    return get_file_objects(file_path).read_file()
