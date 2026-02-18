from typing import Any, Dict, List, Tuple, Callable, Optional

from .errors import SCLSyntaxError, SCLParseError
from .tokens import Token, TokenType
from .document import SCLDocument


class ParserWithComments:

    def __init__(self, tokens: List[Token]):
        self.allTokens = tokens
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
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

    def parseWithComments(self) -> SCLDocument:
        doc = SCLDocument()

        # collect header comment
        headerComments = []
        while self.currentToken().type == TokenType.COMMENT:
            headerComments.append(self.currentToken().value)
            self.pos += 1

        if headerComments:
            doc.setHeaderComment(" ".join(headerComments))

        while self.currentToken().type != TokenType.EOF:
            preComments = []
            while self.currentToken().type == TokenType.COMMENT:
                preComments.append(self.currentToken().value)
                self.pos += 1

            commentBefore = " ".join(preComments) if preComments else None

            if self.currentToken().type == TokenType.EOF:
                break

            name, value = self.parseParameter()
            doc.data[name] = value

            if commentBefore:
                doc.comments[name] = commentBefore

            # inline comm
            if self.currentToken().type == TokenType.COMMENT:
                doc.inlineComments[name] = self.currentToken().value
                self.pos += 1

        return doc

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
            if self.currentToken().type == TokenType.COMMENT:
                self.pos += 1
                continue
            name, value = self.parseParameter()
            obj[name] = value
        self.eat(TokenType.RBRACE)
        return obj

    def _eatOpenBracket(self) -> TokenType:
        tok = self.currentToken()
        if tok.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            return TokenType.LPAREN
        elif tok.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            return TokenType.LBRACKET
        else:
            self.error(f"Expected '(' or '[', got {tok.type.value}")

    def _eatCloseBracket(self, openedWith: TokenType):
        if openedWith == TokenType.LPAREN:
            self.eat(TokenType.RPAREN)
        else:
            self.eat(TokenType.RBRACKET)

    def parseListValue(self) -> List[Any]:
        openedWith = self._eatOpenBracket()
        parserFunc = self._parseListElementType(openedWith)
        self._eatCloseBracket(openedWith)
        self.eat(TokenType.LBRACE)

        elements: List[Any] = []
        while self.currentToken().type != TokenType.RBRACE:
            if self.currentToken().type == TokenType.COMMENT:
                self.pos += 1
                continue
            elements.append(parserFunc())
            if self.currentToken().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            elif self.currentToken().type != TokenType.RBRACE:
                self.error("Expected comma or closing brace")

        self.eat(TokenType.RBRACE)
        return elements

    def _parseListElementType(self, openedWith: TokenType) -> Callable[[], Any]:
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
            innerOpenedWith = self._eatOpenBracket()
            innerParserFunc = self._parseListElementType(innerOpenedWith)
            self._eatCloseBracket(innerOpenedWith)

            def parseNestedList():
                self.eat(TokenType.LBRACE)
                innerElements: List[Any] = []
                while self.currentToken().type != TokenType.RBRACE:
                    if self.currentToken().type == TokenType.COMMENT:
                        self.pos += 1
                        continue
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
