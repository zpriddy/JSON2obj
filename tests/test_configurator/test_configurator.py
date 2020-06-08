#!/usr/bin/python3
"""
test_configurator.py	
"""

from json2obj.ObjectifyConfig.configurator import Configurator


def test_configurator_1():
    configurator = Configurator("tests/files/example_base_template.yaml")
    test_config = configurator.validate_user_config(
        "tests/files/example_user_config.yaml", "tests/files/example_config.yaml", add_missing=True
    )
    assert test_config.parameters.username == "zpriddy"
    assert test_config.options.allow_guests is False
