from typing import Any, Dict, List, Tuple, Callable

from .errors import SCLSyntaxError, SCLParseError
from .tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.COMMENT)]
        self.pos = 0

    def error(self, msg: str):
        token = self.currentToken()
        raise SCLSyntaxError(msg, token.line, token.column)

    def currentToken(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def eat(self, tokenType: TokenType) -> Token:
        token = self.currentToken()
        if token.type != tokenType:
            self.error(f"Expected {tokenType.value}, got {token.type.value}")
        self.pos += 1
        return token

    def parse(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        while self.currentToken().type != TokenType.EOF:
            name, value = self.parseParameter()
            config[name] = value
        return config

    def parseParameter(self) -> Tuple[str, Any]:
        nameToken = self.currentToken()
        if nameToken.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            name = nameToken.value
        elif nameToken.type in (TokenType.BOOL, TokenType.STR, TokenType.NUM,
                                  TokenType.FL, TokenType.ML, TokenType.CLASS, TokenType.LIST, TokenType.DYNAMIC):
            self.pos += 1
            name = nameToken.value
        elif nameToken.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            name = str(nameToken.value)
        elif nameToken.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            name = nameToken.value
        else:
            self.error(f"Expected identifier or keyword, got {nameToken.type.value}")

        self.eat(TokenType.DOUBLE_COLON)

        typeToken = self.currentToken()
        if typeToken.type == TokenType.BOOL:
            self.eat(TokenType.BOOL)
            value = self.parseBoolValue()
        elif typeToken.type == TokenType.STR:
            self.eat(TokenType.STR)
            value = self.parseStrValue()
        elif typeToken.type == TokenType.NUM:
            self.eat(TokenType.NUM)
            value = self.parseNumValue()
        elif typeToken.type == TokenType.FL:
            self.eat(TokenType.FL)
            value = self.parseFlValue()
        elif typeToken.type == TokenType.ML:
            self.eat(TokenType.ML)
            value = self.parseMlValue()
        elif typeToken.type == TokenType.CLASS:
            self.eat(TokenType.CLASS)
            value = self.parseClassValue()
        elif typeToken.type == TokenType.LIST:
            self.eat(TokenType.LIST)
            value = self.parseListValue()
        elif typeToken.type == TokenType.DYNAMIC:
            self.eat(TokenType.DYNAMIC)
            value = self.parseDynamicValue()
        else:
            self.error(f"Unknown type: {typeToken.value}")

        return name, value

    def parseBoolValue(self) -> bool:
        self.eat(TokenType.LBRACE)
        valueToken = self.eat(TokenType.BOOLEAN)
        self.eat(TokenType.RBRACE)
        return valueToken.value

    def parseStrValue(self) -> str:
        self.eat(TokenType.LBRACE)
        tok = self.currentToken()
        if tok.type == TokenType.STRING:
            value = self.eat(TokenType.STRING).value
        elif tok.type == TokenType.PLAIN_STRING:
            value = self.eat(TokenType.PLAIN_STRING).value
        else:
            self.error(f"Expected string value, got {tok.type.value}")
        self.eat(TokenType.RBRACE)
        return value

    def parseNumValue(self) -> int:
        self.eat(TokenType.LBRACE)
        valueToken = self.eat(TokenType.NUMBER)
        self.eat(TokenType.RBRACE)
        return valueToken.value

    def parseFlValue(self) -> float:
        self.eat(TokenType.LBRACE)
        valueToken = self.currentToken()
        if valueToken.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
        elif valueToken.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            valueToken.value = float(valueToken.value)
        else:
            self.error("Expected float or number")
        self.eat(TokenType.RBRACE)
        return valueToken.value

    def parseMlValue(self) -> str:
        self.eat(TokenType.LBRACE)
        tok = self.currentToken()
        if tok.type == TokenType.MULTILINE_STRING:
            value = self.eat(TokenType.MULTILINE_STRING).value
        elif tok.type == TokenType.PLAIN_STRING:
            value = self.eat(TokenType.PLAIN_STRING).value
        else:
            self.error(f"Expected multiline string value, got {tok.type.value}")
        self.eat(TokenType.RBRACE)
        return value

    def parseClassValue(self) -> Dict[str, Any]:
        self.eat(TokenType.LBRACE)
        obj: Dict[str, Any] = {}
        while self.currentToken().type != TokenType.RBRACE:
            name, value = self.parseParameter()
            obj[name] = value
        self.eat(TokenType.RBRACE)
        return obj

    def _eatOpenBracket(self):
        # ( / [
        tok = self.currentToken()
        if tok.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
        elif tok.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
        else:
            self.error(f"Expected '(' or '[', got {tok.type.value}")

    def _eatCloseBracket(self, openedWith: TokenType):
        if openedWith == TokenType.LPAREN:
            self.eat(TokenType.RPAREN)
        else:
            self.eat(TokenType.RBRACKET)

    def parseListValue(self) -> List[Any]:
        openTok = self.currentToken()
        self._eatOpenBracket()
        openedWith = openTok.type
        parserFunc = self._parseListElementType(openedWith)
        self._eatCloseBracket(openedWith)
        self.eat(TokenType.LBRACE)

        elements: List[Any] = []
        while self.currentToken().type != TokenType.RBRACE:
            elements.append(parserFunc())
            if self.currentToken().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            elif self.currentToken().type != TokenType.RBRACE:
                self.error("Expected comma or closing brace")

        self.eat(TokenType.RBRACE)
        return elements

    def _parseListElementType(self, openedWith: TokenType) -> Callable[[], Any]:
        # element type
        elementType = self.currentToken()

        if elementType.type == TokenType.NUM:
            self.eat(TokenType.NUM)
            return lambda: self.eat(TokenType.NUMBER).value
        elif elementType.type == TokenType.FL:
            self.eat(TokenType.FL)
            def parseFloat():
                if self.currentToken().type == TokenType.FLOAT:
                    return float(self.eat(TokenType.FLOAT).value)
                else:
                    return float(self.eat(TokenType.NUMBER).value)
            return parseFloat
        elif elementType.type == TokenType.BOOL:
            self.eat(TokenType.BOOL)
            return lambda: self.eat(TokenType.BOOLEAN).value
        elif elementType.type == TokenType.STR:
            self.eat(TokenType.STR)
            def parseStr():
                tok = self.currentToken()
                if tok.type == TokenType.STRING:
                    return self.eat(TokenType.STRING).value
                elif tok.type == TokenType.PLAIN_STRING:
                    return self.eat(TokenType.PLAIN_STRING).value
                else:
                    self.error(f"Expected string, got {tok.type.value}")
            return parseStr
        elif elementType.type == TokenType.ML:
            self.eat(TokenType.ML)
            def parseMl():
                tok = self.currentToken()
                if tok.type == TokenType.MULTILINE_STRING:
                    return self.eat(TokenType.MULTILINE_STRING).value
                elif tok.type == TokenType.PLAIN_STRING:
                    return self.eat(TokenType.PLAIN_STRING).value
                else:
                    self.error(f"Expected multiline string, got {tok.type.value}")
            return parseMl
        elif elementType.type == TokenType.CLASS:
            self.eat(TokenType.CLASS)
            return self.parseClassValue
        elif elementType.type == TokenType.LIST:
            self.eat(TokenType.LIST)
            innerOpenTok = self.currentToken()
            self._eatOpenBracket()
            innerOpenedWith = innerOpenTok.type
            innerParserFunc = self._parseListElementType(innerOpenedWith)
            self._eatCloseBracket(innerOpenedWith)
            def parseNestedList():
                self.eat(TokenType.LBRACE)
                innerElements: List[Any] = []
                while self.currentToken().type != TokenType.RBRACE:
                    innerElements.append(innerParserFunc())
                    if self.currentToken().type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                    elif self.currentToken().type != TokenType.RBRACE:
                        self.error("Expected comma or closing brace")
                self.eat(TokenType.RBRACE)
                return innerElements
            return parseNestedList
        elif elementType.type == TokenType.DYNAMIC:
            self.eat(TokenType.DYNAMIC)
            return self.parseDynamicValueDirect
        else:
            self.error(f"Unsupported list element type: {elementType.value}")

    def parseDynamicValueDirect(self) -> Any:
        # parse dynamic value without outer braces (for list elements)
        tok = self.currentToken()
        if tok.type == TokenType.NUMBER:
            return self.eat(TokenType.NUMBER).value
        elif tok.type == TokenType.FLOAT:
            return self.eat(TokenType.FLOAT).value
        elif tok.type == TokenType.BOOLEAN:
            return self.eat(TokenType.BOOLEAN).value
        elif tok.type == TokenType.STRING:
            return self.eat(TokenType.STRING).value
        elif tok.type == TokenType.PLAIN_STRING:
            return self.eat(TokenType.PLAIN_STRING).value
        elif tok.type == TokenType.MULTILINE_STRING:
            return self.eat(TokenType.MULTILINE_STRING).value
        else:
            self.error("dynamic supports only base types (bool, str, num, fl, ml)")

    def parseDynamicValue(self) -> Any:
        self.eat(TokenType.LBRACE)
        val = self.parseDynamicValueDirect()
        self.eat(TokenType.RBRACE)
        return val
