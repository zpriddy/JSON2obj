#!/usr/bin/python3
"""
config_class	
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Union

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from ..files import FileTypes, get_file_objects, get_file_type, read_raw_file, write_dict_to_file, write_object_to_file
from ..json2obj import JSON2Obj
from ..json_file import JsonFile
from ..yaml_file import YamlFile
from .config2obj import Config2Obj


class ConfigTypes(str, Enum):
    int = "int"
    float = "float"
    string = "string"
    bool = "bool"
    list = "list"
    string_list = "list.string"
    int_list = "list.int"
    float_list = "list.float"
    bool_list = "list.bool"


def check_value(value: Any, data_type: ConfigTypes):
    def check_bool(v):
        if isinstance(bool, v):
            return value
        if str(v).lower() in ["yes", "y", "true"]:
            return True
        if str(v).lower() in ["no", "n", "false"]:
            return False
        raise TypeError("value is not a boolean")

    def check_list(v):
        if not isinstance(v, list):
            raise TypeError("value is not type list")
        return True

    if data_type is ConfigTypes.int:
        return int(value)

    if data_type is ConfigTypes.float:
        return float(value)

    if data_type is ConfigTypes.string:
        return str(value)

    if data_type is ConfigTypes.bool:
        if isinstance(value, bool):
            return value
        if str(value).lower() in ["yes", "y", "true"]:
            return True
        if str(value).lower() in ["no", "n", "false"]:
            return False
        raise TypeError(f"value is not a boolean: {value}")

    if data_type is ConfigTypes.list:
        if check_list(value):
            return value

    if data_type is ConfigTypes.string_list:
        check_list(value)
        return [str(s) for s in value]

    if data_type is ConfigTypes.bool_list:
        check_list(value)
        return [check_bool(b) for b in value]

    if data_type is ConfigTypes.int_list:
        check_list(value)
        return [int(i) for i in value]

    if data_type is ConfigTypes.float_list:
        check_list(value)
        return [float(f) for f in value]

    raise TypeError("unknown data type")


class ConfigVariable:
    def __init__(
        self,
        name: str,
        type: str,
        description: str = None,
        default=None,
        default_none_okay: bool = False,
        required: bool = False,
        example: str = None,
        meta_data: dict = None,
        **kwargs,
    ):
        self.name = name
        self.data_type: ConfigTypes = ConfigTypes(type)
        self.description = description
        self.default_value = default
        self.default_none_okay = default_none_okay
        self.required = required
        self.example = example
        self.meta_data = JSON2Obj(meta_data, None)
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.value = self.check_value(value)

    def check_value(self, value: Any) -> Any:
        return check_value(value, self.data_type)

    def to_dict(self):
        data = dict(name=self.name, type=self.data_type.value,)
        if self.required:
            data.update(dict(required=self.required))
        if self.default_none_okay:
            data.update(dict(default=self.default_value, default_none_okay=self.default_none_okay))
        for key, val in dict(description=self.description, default=self.default_value, example=self.example).items():
            if val is None:
                continue
            data.update({key: val})
        return data


class ConfigTemplateField:
    def __init__(self, name: str, default: Any = None, required: bool = False, **kwargs):
        self.name = name
        self.default = default
        self.required = required


class ConfigTemplateSection:
    def __init__(self, name: str, type: str, **kwargs):
        self.name = name
        self.section_type = type
        self.fields = None

        if self.section_type == "custom":
            self.fields = dict()
            for field_name, field_value in kwargs.get("fields", dict()).items():
                self.fields[field_name] = ConfigTemplateField(name=field_name, **field_value)

        if self.section_type not in ["custom", "variable"]:
            raise TypeError(f"unknown section type: {self.section_type}")


class ConfigTemplate:
    def __init__(self, file_name: str = None, config: dict = None):
        if file_name:
            config = read_raw_file(file_name)
        self._config_template = config
        self.sections = dict()

        for section in self._sections:
            self.sections[section] = ConfigTemplateSection(name=section, **self._config_template.get(section, {}))

    @property
    def _sections(self) -> List[str]:
        return list(self._config_template.keys())




class DefaultConfigFile:
    def __init__(self, default_config: Union[str, dict], config_template: ConfigTemplate):
        if isinstance(default_config, str):
            default_config = read_raw_file(default_config)

        self.sections = dict()

        for section_name, section_info in config_template.sections.items():
            if section_info.section_type == "custom":
                self.sections[section_name] = default_config.get(section_name)
            if section_info.section_type == "variable":
                for sub_name, sub_value in default_config[section_name].items():
                    if not self.sections.get(section_name):
                        self.sections[section_name] = dict()
                    self.sections[section_name][sub_name] = ConfigVariable(name=sub_name, **sub_value)

    def get_obj(self):
        return JSON2Obj(self.sections)

# TODO: How this should work:
#  ConfigTemplateBase is created for Configurator,
#  Configurator then can load user configs and default configs and validate them returning back a configurator
#  object that then you can request just the user config as a JSON2obj class
