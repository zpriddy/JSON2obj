#!/usr/bin/python3
"""
JSON2Obj

Read a JSON object into a python object
"""
import json
from typing import Callable, Optional

from .env_vars import check_for_env_vars


class JSON2Obj:
    def __init__(self, json_data: dict = None, env_var_function: Optional[Callable] = check_for_env_vars):
        if not isinstance(json_data, dict):
            raise TypeError("json_data must by type dict. If using a string call JSON2Obj.from_string().")

        self.__env_var_function: Callable = env_var_function

        if json_data:
            self.__from_dict(json_data)

    def __eq__(self, other):
        if isinstance(other, JSON2Obj):
            return self.__to_dict() == other.__to_dict()
        return self.__to_dict() == other

    def __dict_fields__(self):
        """Returns a list of fields to get for the to_dict function."""
        fields = list(self.__dict__.keys())
        return [f for f in fields if not f.startswith("__") and not f.startswith("_JSON2Obj")]

    @classmethod
    def from_string(cls, string: str, env_var_function: Optional[Callable] = check_for_env_vars) -> "JSON2Obj":
        """Create a JSON2Obj from a string of a JSON object.

        Args:
            string: JSON input string.
            env_var_function: Function to use for checking for env vars.

        Returns:

        """
        input_dict = json.loads(string)
        return cls(input_dict, env_var_function=env_var_function)

    @classmethod
    def __from_list(cls, input_list: list, env_var_function: Optional[Callable] = check_for_env_vars) -> list:
        """Function for parsing info from a list of data.

        Args:
            input_list: input list to be parsed.

        Returns: A list of parsed data.

        """
        output_list = list()
        for item in input_list:
            if isinstance(item, JSON2Obj):
                output_list.append(item.to_dict())
            elif isinstance(item, dict):
                output_list.append(JSON2Obj.from_dict(item, env_var_function))
            elif isinstance(item, list):
                output_list.append(cls.__from_list(item))
            else:
                output_list.append(item)
        return output_list

    @staticmethod
    def from_dict(input_data: dict, env_var_function: Optional[Callable] = check_for_env_vars):
        """

        Args:
            input_data: Input data for object.
            env_var_function: Function to use for checking for env vars.

        Returns:

        """
        return JSON2Obj(env_var_function=env_var_function).__from_dict(input_data)

    def __from_dict(self, input_data: dict):
        """Set data from a dict.

        Args:
            input_data: dict of input data to set.

        Returns: None

        """
        invalid_keys = ["__from_dict", "__to_dict"]
        for k in invalid_keys:
            if k in input_data:
                raise KeyError(f"invalid input key: {k} in input_data from json")

        for key, value in input_data.items():

            # Check for env_vars here if we have any.
            if self.__env_var_function:
                value = self.__env_var_function(value)

            # If its a dict, make a new JSON2Obj.
            if isinstance(value, dict):
                value = JSON2Obj(value)

            # Go though a list for any new values.
            if isinstance(value, list):
                value = JSON2Obj.__from_list(value)

            setattr(self, key, value)

    @staticmethod
    def to_dict(json_object: "JSON2Obj") -> dict:
        """Output JSON2Obj as a dict.

        Returns: Dict of data stored in the object.

        """
        return json_object.__to_dict()

    def __to_dict(self) -> dict:
        """Output JSON2Obj as a dict.

        Returns: Dict of data stored in the object.

        """
        output = dict()
        fields = self.__dict_fields__()
        for f in fields:
            value = getattr(self, f)
            if isinstance(value, JSON2Obj):
                output[f] = JSON2Obj.to_dict(value)
            else:
                output[f] = value
        return output

    def __repr__(self):
        return str(self.__to_dict())

    @staticmethod
    def get(json_object: "JSON2Obj", key, default=None):
        """Simple get function.

        Args:
            json_object: JSON2Obj object to get the value for.
            key: Key to get value for.
            default: Default value if key is missing. (Default=None)

        Returns: Attribute of the object with the provided key or the default value.

        """
        return getattr(json_object, key, default)
