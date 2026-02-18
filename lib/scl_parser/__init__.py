"""
SCL Parser Library

A Python library for parsing and serializing Structured Configuration Language (SCL) files.
Supports infinite nesting and comment preservation.
"""

from .api import (
    load,
    loads,
    dump,
    dumps,
    loadWithComments,
    loadsWithComments,
    dumpWithComments,
    dumpsWithComments,
    SCLParseError,
    SCLSyntaxError,
)
from .document import SCLDocument

__version__ = "1.2.0"
__author__ = "shareui"
__all__ = [
    "load",
    "loads",
    "dump",
    "dumps",
    "loadWithComments",
    "loadsWithComments",
    "dumpWithComments",
    "dumpsWithComments",
    "SCLDocument",
    "SCLParseError",
    "SCLSyntaxError",
]
