#!/usr/bin/python3
"""
env_vars.py	
"""
import os
from base64 import b64decode
from typing import Union


def decode_kms(ciphertext_blob: str) -> str:
    """Decode a secret using the IAM role of the lambda function.

    Args:
        ciphertext_blob: ciphertext_blob to decode

    Returns: Decoded KMS data

    """
    try:
        import boto3
    except ImportError:
        raise ImportError("Missing bot3 package required for KMS.")

    return boto3.client("kms").decrypt(CiphertextBlob=b64decode(ciphertext_blob))["Plaintext"].decode("utf-8")


def get_kms_var(var_name: str) -> str:
    """Get an encrypted ENV VAR"""
    ciphertext_blob = get_var(var_name)
    return decode_kms(ciphertext_blob)


def check_for_env_vars(value: Union[str, dict]):
    """Check an input value to see if it is an env_var or enc_env_var and get the value.

    Args:
        value: input value to check.

    Returns: The value of the var from either the passed in value, or the env var value.

    Raises:
        KeyError: if the env var is not set for what you're tying to get.

    """
    if type(value) is dict and "env_var" in value:
        var_name = value["env_var"]
        try:
            return get_var(var_name)
        except KeyError:
            raise KeyError(f"missing env var: {value['env_var']}")
    if type(value) is dict and "enc_env_var" in value:
        var_name = value["enc_env_var"]
        try:
            return get_kms_var(var_name)
        except KeyError:
            raise KeyError(f"missing enc env var: {value['enc_env_var']}")
    return value


def get_var(var_name: str):
    """Get an env var.

    Args:
        var_name: Var name to get.

    Returns: value of the env var.

    """
    return os.environ[var_name]
