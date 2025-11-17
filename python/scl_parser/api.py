from typing import Any, Dict

from .errors import SCLParseError, SCLSyntaxError
from .lexer import Lexer
from .parser_core import Parser
from .serializer import Serializer

__version__ = "1.0.1"
__author__ = "shareui"
__all__ = ["load", "loads", "dump", "dumps", "SCLParseError", "SCLSyntaxError"]

def loads(text: str) -> Dict[str, Any]:
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def load(filename: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    with open(filename, 'r', encoding=encoding) as f:
        text = f.read()
    return loads(text)


def dumps(data: Dict[str, Any], indent: int = 4) -> str:
    serializer = Serializer(indent=indent)
    return serializer.serialize(data)


def dump(data: Dict[str, Any], filename: str, indent: int = 4, encoding: str = 'utf-8'):
    text = dumps(data, indent=indent)
    with open(filename, 'w', encoding=encoding) as f:
        f.write(text)


