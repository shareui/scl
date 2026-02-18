from typing import Any, List, Optional

from .errors import SCLSyntaxError
from .tokens import Token, TokenType


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, msg: str):
        raise SCLSyntaxError(msg, self.line, self.column)

    def peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return None

    def advance(self) -> Optional[str]:
        if self.pos < len(self.text):
            char = self.text[self.pos]
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return None

    def skip_whitespace(self):
        while self.peek() in ' \t':
            self.advance()

    def _last_significant_type(self) -> Optional[TokenType]:
        # returns last token type ignoring newlines/comments
        for tok in reversed(self.tokens):
            if tok.type not in (TokenType.NEWLINE, TokenType.COMMENT):
                return tok.type
        return None

    def _is_list_bracket_context(self) -> bool:
        lastType = self._last_significant_type()
        return lastType in (TokenType.LIST, TokenType.RBRACKET)

    def _is_plain_string_context(self) -> bool:
        # plain string
        significant = [t for t in self.tokens if t.type not in (TokenType.NEWLINE, TokenType.COMMENT)]
        if len(significant) < 2:
            return False
        return (significant[-1].type == TokenType.LBRACE and
                significant[-2].type in (TokenType.STR, TokenType.ML))

    def read_comment(self) -> Token:
        start_line = self.line
        start_col = self.column
        self.advance()
        comment = ""
        while self.peek() and self.peek() != ']':
            comment += self.advance()
        if self.peek() != ']':
            self.error("Unclosed comment")
        self.advance()
        return Token(TokenType.COMMENT, comment.strip(), start_line, start_col)

    def _read_escape(self) -> str:
        nextChar = self.peek()
        if nextChar is None:
            self.error("Unexpected end of input after backslash")
        if nextChar == 'n':
            self.advance()
            return '\n'
        if nextChar == 't':
            self.advance()
            return '\t'
        if nextChar == '\\':
            self.advance()
            return '\\'
        if nextChar == '"':
            self.advance()
            return '"'
        if nextChar == "'":
            self.advance()
            return "'"
        if nextChar == 'u':
            # \uXXXX
            self.advance()
            hexDigits = ""
            for _ in range(4):
                ch = self.peek()
                if ch is None or ch not in '0123456789abcdefABCDEF':
                    self.error("Invalid unicode escape: expected 4 hex digits")
                hexDigits += self.advance()
            return chr(int(hexDigits, 16))
        return self.advance()

    def read_string(self) -> Token:
        start_line = self.line
        start_col = self.column
        self.advance()
        string = ""
        while self.peek() and self.peek() != '"':
            if self.peek() == '\\':
                self.advance()
                string += self._read_escape()
            else:
                string += self.advance()
        if self.peek() != '"':
            self.error("Unclosed string")
        self.advance()
        return Token(TokenType.STRING, string, start_line, start_col)

    def read_multiline_string(self) -> Token:
        start_line = self.line
        start_col = self.column
        self.advance()
        string = ""
        while self.peek() and self.peek() != "'":
            if self.peek() == '\\':
                self.advance()
                string += self._read_escape()
            else:
                string += self.advance()
        if self.peek() != "'":
            self.error("Unclosed multiline string")
        self.advance()
        return Token(TokenType.MULTILINE_STRING, string, start_line, start_col)

    def read_plain_string(self) -> Token:
        # plain string: everything until } (trimmed), no escape processing
        start_line = self.line
        start_col = self.column
        string = ""
        while self.peek() and self.peek() != '}':
            string += self.advance()
        return Token(TokenType.PLAIN_STRING, string.strip(), start_line, start_col)

    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        number = ""
        if self.peek() == '-':
            number += self.advance()
            if not self.peek() or not self.peek().isdigit():
                self.error("Expected digit after '-'")

        has_dot = False
        has_digits_before_dot = False
        has_digits_after_dot = False

        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            if self.peek() == '.':
                if has_dot:
                    break
                has_dot = True
                number += self.advance()
            else:
                number += self.advance()
                if has_dot:
                    has_digits_after_dot = True
                else:
                    has_digits_before_dot = True

        if not has_digits_before_dot and not has_digits_after_dot:
            self.error("Invalid number format")

        if has_dot:
            return Token(TokenType.FLOAT, float(number), start_line, start_col)
        else:
            return Token(TokenType.NUMBER, int(number), start_line, start_col)

    def read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.column
        identifier = ""
        while self.peek() and (self.peek().isalnum() or self.peek() in ('_', '-')):
            identifier += self.advance()

        keywords = {
            "bool": TokenType.BOOL,
            "str": TokenType.STR,
            "num": TokenType.NUM,
            "fl": TokenType.FL,
            "ml": TokenType.ML,
            "class": TokenType.CLASS,
            "list": TokenType.LIST,
            "dynamic": TokenType.DYNAMIC,
        }
        boolean_values = {
            "true": True,
            "false": False,
            "yes": True,
            "no": False,
        }

        if identifier in keywords:
            return Token(keywords[identifier], identifier, start_line, start_col)
        elif identifier in boolean_values:
            return Token(TokenType.BOOLEAN, boolean_values[identifier], start_line, start_col)
        else:
            return Token(TokenType.IDENTIFIER, identifier, start_line, start_col)

    def read_identifier_with_digits(self) -> Token:
        start_line = self.line
        start_col = self.column
        identifier = ""
        while self.peek() and (self.peek().isalnum() or self.peek() in ('_', '-')):
            identifier += self.advance()
        return Token(TokenType.IDENTIFIER, identifier, start_line, start_col)

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.text):
            self.skip_whitespace()
            if self.peek() is None:
                break

            if self.peek() == '[':
                if self._is_list_bracket_context():
                    start_col = self.column
                    self.advance()
                    self.tokens.append(Token(TokenType.LBRACKET, '[', self.line, start_col))
                else:
                    self.tokens.append(self.read_comment())
                continue

            if self.peek() == ']':
                start_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', self.line, start_col))
                continue

            if self.peek() == '\n':
                newline_line = self.line
                newline_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', newline_line, newline_col))
                continue

            if self.peek() == ':' and self.peek(1) == ':':
                start_col = self.column
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.DOUBLE_COLON, '::', self.line, start_col))
                continue

            if self.peek() in '{}(),':
                start_col = self.column
                ch = self.advance()
                ttype = {
                    '{': TokenType.LBRACE,
                    '}': TokenType.RBRACE,
                    '(': TokenType.LPAREN,
                    ')': TokenType.RPAREN,
                    ',': TokenType.COMMA
                }[ch]
                self.tokens.append(Token(ttype, ch, self.line, start_col))
                continue

            if self.peek() == '"':
                self.tokens.append(self.read_string())
                continue

            if self.peek() == "'":
                self.tokens.append(self.read_multiline_string())
                continue

            # plain string again
            if self._is_plain_string_context():
                self.tokens.append(self.read_plain_string())
                continue

            if self.peek() == '-' and self.peek(1) and self.peek(1).isdigit():
                self.tokens.append(self.read_number())
                continue

            if self.peek().isdigit():
                peek_ahead = self.pos + 1
                while peek_ahead < len(self.text) and self.text[peek_ahead].isdigit():
                    peek_ahead += 1
                if peek_ahead < len(self.text) and (self.text[peek_ahead].isalpha() or self.text[peek_ahead] == '_'):
                    self.tokens.append(self.read_identifier_with_digits())
                else:
                    self.tokens.append(self.read_number())
                continue

            if self.peek().isalpha() or self.peek() == '_':
                self.tokens.append(self.read_identifier())
                continue

            self.error(f"Unexpected character: {self.peek()}")

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
