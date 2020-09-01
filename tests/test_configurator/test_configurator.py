#!/usr/bin/python3
"""
test_configurator.py	
"""

from json2obj.ObjectifyConfig.configurator import Configurator


def test_configurator_1():
    # TODO: Make this a ficture
    configurator = Configurator("tests/files/example_base_template.yaml")
    test_config = configurator.validate_user_config(
        "tests/files/example_user_config.yaml", "tests/files/example_config.yaml", add_missing=True
    )
    assert test_config.parameters.username == "zpriddy"
    assert test_config.options.allow_guests is False

    # TODO: Dont have this in this test
    z = configurator.read_default_config("tests/files/example_config.yaml").get_obj()
    assert z.options.start_on_login.metadata == {"value1": 123}
