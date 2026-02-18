from typing import Any, Dict, Union

from .errors import SCLParseError, SCLSyntaxError
from .lexer import Lexer
from .parser_core import Parser
from .parser_with_comments import ParserWithComments
from .serializer import Serializer
from .document import SCLDocument

__version__ = "1.2.0"
__author__ = "shareui"
__all__ = [
    "load", "loads", "dump", "dumps",
    "loadWithComments", "loadsWithComments", "dumpWithComments", "dumpsWithComments",
    "SCLDocument",
    "SCLParseError", "SCLSyntaxError"
]


def loads(text: str) -> Dict[str, Any]:
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def load(filename: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    with open(filename, 'r', encoding=encoding) as f:
        text = f.read()
    return loads(text)


def loadsWithComments(text: str) -> SCLDocument:
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = ParserWithComments(tokens)
    return parser.parseWithComments()


def loadWithComments(filename: str, encoding: str = 'utf-8') -> SCLDocument:
    with open(filename, 'r', encoding=encoding) as f:
        text = f.read()
    return loadsWithComments(text)


def dumps(data: Union[Dict[str, Any], SCLDocument], indent: int = 4) -> str:
    serializer = Serializer(indent=indent)
    return serializer.serialize(data)


def dump(data: Union[Dict[str, Any], SCLDocument], filename: str, indent: int = 4, encoding: str = 'utf-8'):
    text = dumps(data, indent=indent)
    with open(filename, 'w', encoding=encoding) as f:
        f.write(text)


def dumpsWithComments(doc: SCLDocument, indent: int = 4) -> str:
    if not isinstance(doc, SCLDocument):
        raise TypeError("dumpsWithComments requires SCLDocument, use dumps() for dict")
    return dumps(doc, indent=indent)


def dumpWithComments(doc: SCLDocument, filename: str, indent: int = 4, encoding: str = 'utf-8'):
    if not isinstance(doc, SCLDocument):
        raise TypeError("dumpWithComments requires SCLDocument, use dump() for dict")
    dump(doc, filename, indent=indent, encoding=encoding)
