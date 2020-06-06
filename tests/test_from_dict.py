#!/usr/bin/python3
"""
test_from_dict.py	
"""
from json2obj.json2obj import JSON2Obj


def test_from_dict_1():
    input_dict = dict(key1="value1", key2=dict(key2a="value2a", key2b="value2b"), key3="value3")
    json_obj = JSON2Obj(input_dict)
    assert json_obj.key2.key2a == "value2a"


def test_from_dict_2():
    input_dict = dict(key1="value1", key2=["value2a", "value2b"], key3="value3")
    json_obj = JSON2Obj(input_dict, env_var_function=None)
    assert json_obj.key2 == ["value2a", "value2b"]


def test_from_dict_3():
    input_dict = dict(key1="value1", key2=["value2", ["value2a", "value2b"]], key3="value3")
    json_obj = JSON2Obj(input_dict)
    assert json_obj.key2[1] == ["value2a", "value2b"]


def test_from_dict_4():
    input_dict = dict(key1="value1", key2=["value2", ["value2a", "value2b"]], key3="value3")
    json_obj = JSON2Obj(input_dict)
    assert JSON2Obj.get(json_obj, "key1") == "value1"


def test_from_dict_5():
    input_dict = dict(get="value1", key2=["value2", ["value2a", "value2b"]], key3="value3")
    json_obj = JSON2Obj(input_dict)
    assert JSON2Obj.get(json_obj, "get") == "value1"
