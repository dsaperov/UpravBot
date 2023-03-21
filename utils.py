import os

from exceptions import UnconfiguredEnvironmentError


def getenv_or_throw_exception(var_name):
    value = os.getenv(var_name)
    if not value:
        raise UnconfiguredEnvironmentError(var_name)
    return value
