from typing import Optional


class SCLParseError(Exception):
    pass


class SCLSyntaxError(SCLParseError):
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        if line and column:
            super().__init__(f"Syntax error at line {line}, column {column}: {message}")
        else:
            super().__init__(f"Syntax error: {message}")


