from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    DOUBLE_COLON = "::"
    BOOL = "bool"
    STR = "str"
    NUM = "num"
    FL = "fl"
    ML = "ml"
    CLASS = "class"
    LIST = "list"
    DYNAMIC = "dynamic"
    LBRACE = "{"
    RBRACE = "}"
    LPAREN = "("
    RPAREN = ")"
    COMMA = ","
    STRING = "STRING"
    MULTILINE_STRING = "MULTILINE_STRING"
    NUMBER = "NUMBER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    COMMENT = "COMMENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int


