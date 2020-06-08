#!/usr/bin/python3
"""
configurator.py	
"""
import logging
from pathlib import Path
from typing import Dict, Union

from ruamel.yaml.comments import CommentedMap

from ..files import FileTypes, get_file_objects, get_file_type, read_raw_file, write_object_to_file
from ..json2obj import JSON2Obj
from ..yaml_file import YamlFile
from .config_class import ConfigTemplate, DefaultConfigFile, ConfigVariable


class Configurator:
    def __init__(self, config_template: Union[str, ConfigTemplate, dict], **kwargs):
        """Start a Configurator.

        Args:
            config_template: dict to path to config template file.
            **kwargs:
        """
        if isinstance(config_template, str):
            self.config_template = ConfigTemplate(file_name=config_template)
        if isinstance(config_template, dict):
            self.config_template = ConfigTemplate(config=config_template)
        if isinstance(config_template, ConfigTemplate):
            self.config_template = config_template

    def check_default_config(self, default_config: Union[str, dict]):
        """Check the default config against the base config template.

        Args:
            default_config: File path or config as a dict

        Returns:

        """
        if isinstance(default_config, str):
            default_config = read_raw_file(default_config)

        for section_name, section_val in self.config_template.sections.items():
            if section_name not in default_config:
                raise KeyError(f"default config missing section {section_name}")
            if section_val.section_type == "custom":
                missing_fields = [
                    field
                    for field in list(self.config_template.sections[section_name].fields.keys())
                    if field not in default_config[section_name]
                    and self.config_template.sections[section_name].fields[field].required
                ]
                if missing_fields:
                    raise KeyError(f"missing custom field(s): {missing_fields}")
        return True

    def read_default_config(self, default_config: Union[str, dict]):
        """Read the default config into a JSON2Obj object.

        Args:
            default_config:

        Returns:

        """
        if isinstance(default_config, str):
            default_config = read_raw_file(default_config)
        self.check_default_config(default_config)

        default_config = DefaultConfigFile(default_config, self.config_template)
        return default_config

    @staticmethod
    def get_user_config(user_config: Union[str, dict]) -> dict:
        """Get user_config from an object as a dict

        Args:
            user_config:

        Returns:

        """
        if isinstance(user_config, str):
            user_config = JSON2Obj.to_dict(get_file_objects(user_config).load())
        if isinstance(user_config, dict):
            return user_config
        raise TypeError("invalid type for user config")

    def validate_user_config(
        self,
        user_config: Union[str, dict],
        default_config: Union[str, dict],
        add_missing: bool = True,
        ignore_required: bool = False,
    ) -> JSON2Obj:
        """Validate the user config based off of the default config.

        Notes:
            This will also add default values to the user_config from the default_config if they are missing and not
            marked as required.

        Args:
            user_config: Dict of user config or path to JSON or YAML file.
            default_config: Dict of default config or path to JSON or YAML file.
            add_missing: If True add the default values to the user config if they are missing.
            ignore_required: If True ignore required values. This is used for updating a config file.

        Returns: Validated user config as a JSON2Obj

        """
        user_config = self.get_user_config(user_config)
        default_config = self.read_default_config(default_config)

        for section_name, section_info in JSON2Obj.to_dict(default_config.get_obj()).items():
            if (
                section_name not in user_config
                and self.config_template.sections[section_name].section_type == "variable"
            ):
                var_config: Dict[str, ConfigVariable] = JSON2Obj.to_dict(
                    JSON2Obj.get(default_config.get_obj(), section_name)
                )
                any_required = any(val.required is True for key, val in var_config.items())

                if (add_missing and not any_required) or ignore_required:
                    user_config[section_name] = dict()
                else:
                    if any_required:
                        raise KeyError(f"user config file missing section: {section_name}")
                    else:
                        user_config[section_name] = dict()

            if self.config_template.sections[section_name].section_type == "custom":
                # NOTE: We do not validate here because some things like metadata may only need to be in the plugin
                #  config and not in the user config. Below is code to validate this if it were to change in the future.

                # for sub_name, sub_val in self.config_template.sections[section_name].fields.items():
                #     if sub_val.required and sub_name not in user_config.get(section_name, {}):
                #         raise KeyError(f"user_config section: {section_name} missing required field: {sub_val.name}")
                pass
            elif self.config_template.sections[section_name].section_type == "variable":
                var_config: Dict[str, ConfigVariable] = JSON2Obj.to_dict(
                    JSON2Obj.get(default_config.get_obj(), section_name)
                )
                for sub_name, sub_val in var_config.items():
                    value = user_config.get(section_name, {}).get(sub_name)
                    if add_missing:
                        if value and sub_val.default_none_okay is not False:
                            value = sub_val.check_value(value)
                        if value is None and sub_val.default_none_okay is not True:
                            value = sub_val.default_value
                    else:
                        value = sub_val.check_value(value)
                        if value:
                            logging.debug(f"value {value} is valid for {sub_val.data_type}")
                        elif ignore_required:
                            logging.warning(
                                f"value {sub_val.default_value} added to field {sub_name} but is marked as required."
                            )
                            value = sub_val.default_value
                        elif sub_val.required and not sub_val.default_none_okay:
                            raise ValueError(f"missing required value: {sub_name}")
                    user_config[section_name].update({sub_name: value})

        return JSON2Obj(user_config)

    def _add_comments_and_examples(self, sample_config: YamlFile, default_config: str) -> CommentedMap:
        """Add comments and examples for the sample config file.

        Args:
            sample_config:
            default_config:

        Returns:

        """
        default_config = self.read_default_config(default_config)
        default_config_dict = JSON2Obj.to_dict(default_config.get_obj())
        sample_config_raw: CommentedMap = sample_config.read_file()
        for section_name, section_info in default_config_dict.items():
            if self.config_template.sections[section_name].section_type == "custom":
                continue

            var_config: Dict[str, ConfigVariable] = JSON2Obj.to_dict(
                JSON2Obj.get(default_config.get_obj(), section_name)
            )

            sample_config_raw.yaml_set_comment_before_after_key(section_name, before="\n")

            for key, val in var_config.items():
                sample_config_raw[section_name].yaml_set_comment_before_after_key(key, f"\n{val.description}", indent=2)

                if val.default_value is None:
                    sample_config_raw[section_name].yaml_set_comment_before_after_key(
                        key, f"This is a required value [{key}]", indent=4
                    )

                else:
                    sample_config_raw[section_name].update({key: val.default_value})
                    sample_config_raw[section_name].yaml_set_comment_before_after_key(
                        key, f"This is a default value", indent=4
                    )

                if val.example:
                    print(f"{section_name}[{key}] : {val.example}")
                    sample_config_raw[section_name].yaml_set_comment_before_after_key(
                        key, f"example: {val.example}", indent=4
                    )
        return sample_config_raw

    def create_sample_config_file(
        self, sample_config_path: str, default_config: Union[str, dict], overwrite: bool = False
    ):
        """Generate a sample config file based on the default config.

        Args:
            sample_config_path: Path to save sample config output file.
            default_config: Path to default config file.
            overwrite: Overwrite sample_config_path file if the file exists.

        Returns: None

        """
        user_config_file = Path(sample_config_path)
        if user_config_file.exists():
            if not overwrite:
                raise FileExistsError(f"user config file at {str(user_config_file)} exists.")
        else:
            user_config_file.touch()

        sample_config = self.validate_user_config(
            user_config={}, default_config=default_config, add_missing=True, ignore_required=True
        )

        write_object_to_file(sample_config, sample_config_path, rebase=False, env_var_function=None)

        if get_file_type(sample_config_path) is FileTypes.YAML:
            yaml_file = YamlFile(sample_config_path)
            sample_comments = self._add_comments_and_examples(yaml_file, default_config)
            yaml_file.write_file(sample_comments, False)
