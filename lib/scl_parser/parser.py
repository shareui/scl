# pub api
from typing import Any, Dict

from .api import load, loads, dump, dumps
from .errors import SCLParseError, SCLSyntaxError

__version__ = "1.2.0"
__author__ = "shareui"
__all__ = ["load", "loads", "dump", "dumps", "SCLParseError", "SCLSyntaxError"]
