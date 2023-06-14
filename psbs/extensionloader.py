from psbs.extensions import *
from .extension import Extension


def get_extensions():
    return Extension.__subclasses__()
