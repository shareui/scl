from typing import Any, Dict, List, Tuple

from .errors import SCLSyntaxError, SCLParseError
from .tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.COMMENT)]
        self.pos = 0
    
    def error(self, msg: str):
        token = self.current_token()
        raise SCLSyntaxError(msg, token.line, token.column)
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]
    
    def eat(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type.value}, got {token.type.value}")
        self.pos += 1
        return token
    
    def parse(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        while self.current_token().type != TokenType.EOF:
            name, value = self.parse_parameter()
            config[name] = value
        return config
    
    def parse_parameter(self) -> Tuple[str, Any]:
        name_token = self.current_token()
        if name_token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            name = name_token.value
        elif name_token.type in (TokenType.BOOL, TokenType.STR, TokenType.NUM, 
                                  TokenType.FL, TokenType.ML, TokenType.CLASS, TokenType.LIST, TokenType.DYNAMIC):
            self.pos += 1
            name = name_token.value
        elif name_token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            name = str(name_token.value)
        elif name_token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            name = name_token.value
        else:
            self.error(f"Expected identifier or keyword, got {name_token.type.value}")
        
        self.eat(TokenType.DOUBLE_COLON)
        
        type_token = self.current_token()
        if type_token.type == TokenType.BOOL:
            self.eat(TokenType.BOOL)
            value = self.parse_bool_value()
        elif type_token.type == TokenType.STR:
            self.eat(TokenType.STR)
            value = self.parse_str_value()
        elif type_token.type == TokenType.NUM:
            self.eat(TokenType.NUM)
            value = self.parse_num_value()
        elif type_token.type == TokenType.FL:
            self.eat(TokenType.FL)
            value = self.parse_fl_value()
        elif type_token.type == TokenType.ML:
            self.eat(TokenType.ML)
            value = self.parse_ml_value()
        elif type_token.type == TokenType.CLASS:
            self.eat(TokenType.CLASS)
            value = self.parse_class_value()
        elif type_token.type == TokenType.LIST:
            self.eat(TokenType.LIST)
            value = self.parse_list_value()
        elif type_token.type == TokenType.DYNAMIC:
            self.eat(TokenType.DYNAMIC)
            value = self.parse_dynamic_value()
        else:
            self.error(f"Unknown type: {type_token.value}")
        
        return name, value
    
    def parse_bool_value(self) -> bool:
        self.eat(TokenType.LBRACE)
        value_token = self.eat(TokenType.BOOLEAN)
        self.eat(TokenType.RBRACE)
        return value_token.value
    
    def parse_str_value(self) -> str:
        self.eat(TokenType.LBRACE)
        value_token = self.eat(TokenType.STRING)
        self.eat(TokenType.RBRACE)
        return value_token.value
    
    def parse_num_value(self) -> int:
        self.eat(TokenType.LBRACE)
        value_token = self.eat(TokenType.NUMBER)
        self.eat(TokenType.RBRACE)
        return value_token.value
    
    def parse_fl_value(self) -> float:
        self.eat(TokenType.LBRACE)
        value_token = self.current_token()
        if value_token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
        elif value_token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            value_token.value = float(value_token.value)
        else:
            self.error("Expected float or number")
        self.eat(TokenType.RBRACE)
        return value_token.value
    
    def parse_ml_value(self) -> str:
        self.eat(TokenType.LBRACE)
        value_token = self.eat(TokenType.MULTILINE_STRING)
        self.eat(TokenType.RBRACE)
        return value_token.value
    
    def parse_class_value(self) -> Dict[str, Any]:
        self.eat(TokenType.LBRACE)
        obj: Dict[str, Any] = {}
        while self.current_token().type != TokenType.RBRACE:
            name, value = self.parse_parameter()
            obj[name] = value
        self.eat(TokenType.RBRACE)
        return obj
    
    def parse_list_value(self) -> List[Any]:
        self.eat(TokenType.LPAREN)
        element_type = self.current_token()
        
        if element_type.type == TokenType.NUM:
            self.eat(TokenType.NUM)
            parser_func = lambda: self.eat(TokenType.NUMBER).value
        elif element_type.type == TokenType.FL:
            self.eat(TokenType.FL)
            def parse_float():
                if self.current_token().type == TokenType.FLOAT:
                    return float(self.eat(TokenType.FLOAT).value)
                else:
                    return float(self.eat(TokenType.NUMBER).value)
            parser_func = parse_float
        elif element_type.type == TokenType.BOOL:
            self.eat(TokenType.BOOL)
            parser_func = lambda: self.eat(TokenType.BOOLEAN).value
        elif element_type.type == TokenType.STR:
            self.eat(TokenType.STR)
            parser_func = lambda: self.eat(TokenType.STRING).value
        else:
            self.error(f"Unsupported list element type: {element_type.value}")
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        elements: List[Any] = []
        while self.current_token().type != TokenType.RBRACE:
            elements.append(parser_func())
            if self.current_token().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            elif self.current_token().type != TokenType.RBRACE:
                self.error("Expected comma or closing brace")
        
        self.eat(TokenType.RBRACE)
        return elements
    
    def parse_dynamic_value(self) -> Any:
        self.eat(TokenType.LBRACE)
        tok = self.current_token()
        if tok.type in (TokenType.NUMBER, TokenType.FLOAT, TokenType.BOOLEAN, TokenType.STRING, TokenType.MULTILINE_STRING):
            if tok.type == TokenType.NUMBER:
                val = self.eat(TokenType.NUMBER).value
            elif tok.type == TokenType.FLOAT:
                val = self.eat(TokenType.FLOAT).value
            elif tok.type == TokenType.BOOLEAN:
                val = self.eat(TokenType.BOOLEAN).value
            elif tok.type == TokenType.STRING:
                val = self.eat(TokenType.STRING).value
            else:
                val = self.eat(TokenType.MULTILINE_STRING).value
        else:
            self.error("dynamic supports only base types (bool, str, num, fl, ml)")
        self.eat(TokenType.RBRACE)
        return val


