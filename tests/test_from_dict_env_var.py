#!/usr/bin/python3
"""
test_from_dict_env_var.py	
"""

from json2obj.json2obj import JSON2Obj
from os import environ
import pytest


def test_from_dict_env_var_1():
    environ["my_var"] = "3"
    input_dict = dict(key1=dict(env_var="my_var"), key2=dict(key2a="value2a", key2b="value2b"), key3="value3")
    json_obj = JSON2Obj(input_dict)
    assert json_obj.key1 == "3"



def test_from_dict_env_var_2():
    environ["my_var"] = "3"
    input_dict = dict(key1=dict(env_var="my_vars"), key2=dict(key2a="value2a", key2b="value2b"), key3="value3")
    with pytest.raises(KeyError):
        json_obj = JSON2Obj(input_dict)
