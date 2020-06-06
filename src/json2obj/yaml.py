#!/usr/bin/python3
"""
yaml.py	
"""

from typing import Callable, Optional

import yaml

from .env_vars import check_for_env_vars
from .json2obj import JSON2Obj


def read_yaml_file(file_path: str, env_var_function: Optional[Callable] = check_for_env_vars) -> JSON2Obj:
    """Read a yaml file into a JSON2Obj.

    Args:
        file_path: Full path to file.
        env_var_function: Function to use for checking for env vars.

    Returns: JSON2Obj of yaml file.

    """
    with open(file_path) as file:
        data = yaml.load(file, yaml.FullLoader)
        json_obj = JSON2Obj(data, env_var_function=env_var_function)
        return json_obj
