"""
Backwards-compatible shim exposing the public API via modular implementation.
"""
from typing import Any, Dict

from .api import load, loads, dump, dumps
from .errors import SCLParseError, SCLSyntaxError

__version__ = "1.0.1"
__author__ = "shareui"
__all__ = ["load", "loads", "dump", "dumps", "SCLParseError", "SCLSyntaxError"]
