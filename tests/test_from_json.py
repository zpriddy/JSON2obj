#!/usr/bin/python3
"""
test_from_yaml.py	
"""
from json2obj import JSON2Obj, read_json_file


def test_load_from_yaml():
    my_config = read_json_file("tests/files/test_file_1.json")
    assert my_config.allow_access is True
    assert my_config.custom.items == ["a", "b", "c"]
