"""
SCL Parser Library

A Python library for parsing and serializing Structured Configuration Language (SCL) files.
"""

from .api import (
    load,
    loads,
    dump,
    dumps,
    SCLParseError,
    SCLSyntaxError,
)

__version__ = "1.0.1"
__author__ = "shareui"
__all__ = ["load", "loads", "dump", "dumps", "SCLParseError", "SCLSyntaxError"]