package scl

import "fmt"

type Parser struct {
    tokens []Token
    pos    int
}

func NewParser(tokens []Token) *Parser {
    filtered := make([]Token, 0)
    for _, t := range tokens {
        if t.Type != TokenNewline && t.Type != TokenComment {
            filtered = append(filtered, t)
        }
    }
    return &Parser{
        tokens: filtered,
        pos:    0,
    }
}

func (p *Parser) currentToken() Token {
    if p.pos < len(p.tokens) {
        return p.tokens[p.pos]
    }
    return p.tokens[len(p.tokens)-1]
}

func (p *Parser) eat(tokenType TokenType) Token {
    token := p.currentToken()
    if token.Type != tokenType {
        panic(newSyntaxError(fmt.Sprintf("Expected %s, got %s", tokenType, token.Type), token.Line, token.Column))
    }
    p.pos++
    return token
}

func (p *Parser) Parse() (map[string]interface{}, error) {
    defer func() {
        if r := recover(); r != nil {
            if err, ok := r.(*SyntaxError); ok {
                panic(err)
            }
            panic(r)
        }
    }()

    config := make(map[string]interface{})
    for p.currentToken().Type != TokenEOF {
        name, value := p.parseParameter()
        config[name] = value
    }
    return config, nil
}

func (p *Parser) parseParameter() (string, interface{}) {
    nameToken := p.currentToken()
    var name string

    switch nameToken.Type {
    case TokenIdentifier, TokenBool, TokenStr, TokenNum, TokenFl, TokenMl, TokenClass, TokenList, TokenDynamic:
        p.pos++
        name = nameToken.Value.(string)
    case TokenNumber:
        p.eat(TokenNumber)
        name = fmt.Sprintf("%d", nameToken.Value.(int))
    case TokenString:
        p.eat(TokenString)
        name = nameToken.Value.(string)
    default:
        panic(newSyntaxError(fmt.Sprintf("Expected identifier or keyword, got %s", nameToken.Type), nameToken.Line, nameToken.Column))
    }

    p.eat(TokenDoubleColon)

    typeToken := p.currentToken()
    var value interface{}

    switch typeToken.Type {
    case TokenBool:
        p.eat(TokenBool)
        value = p.parseBoolValue()
    case TokenStr:
        p.eat(TokenStr)
        value = p.parseStrValue()
    case TokenNum:
        p.eat(TokenNum)
        value = p.parseNumValue()
    case TokenFl:
        p.eat(TokenFl)
        value = p.parseFlValue()
    case TokenMl:
        p.eat(TokenMl)
        value = p.parseMlValue()
    case TokenClass:
        p.eat(TokenClass)
        value = p.parseClassValue()
    case TokenList:
        p.eat(TokenList)
        value = p.parseListValue()
    case TokenDynamic:
        p.eat(TokenDynamic)
        value = p.parseDynamicValue()
    default:
        panic(newSyntaxError(fmt.Sprintf("Unknown type: %s", typeToken.Value), typeToken.Line, typeToken.Column))
    }

    return name, value
}

func (p *Parser) parseBoolValue() bool {
    p.eat(TokenLBrace)
    valueToken := p.eat(TokenBoolean)
    p.eat(TokenRBrace)
    return valueToken.Value.(bool)
}

func (p *Parser) parseStrValue() string {
    p.eat(TokenLBrace)
    valueToken := p.eat(TokenString)
    p.eat(TokenRBrace)
    return valueToken.Value.(string)
}

func (p *Parser) parseNumValue() int {
    p.eat(TokenLBrace)
    valueToken := p.eat(TokenNumber)
    p.eat(TokenRBrace)
    return valueToken.Value.(int)
}

func (p *Parser) parseFlValue() float64 {
    p.eat(TokenLBrace)
    valueToken := p.currentToken()
    var value float64
    if valueToken.Type == TokenFloat {
        p.eat(TokenFloat)
        value = valueToken.Value.(float64)
    } else if valueToken.Type == TokenNumber {
        p.eat(TokenNumber)
        value = float64(valueToken.Value.(int))
    } else {
        panic(newSyntaxError("Expected float or number", valueToken.Line, valueToken.Column))
    }
    p.eat(TokenRBrace)
    return value
}

func (p *Parser) parseMlValue() string {
    p.eat(TokenLBrace)
    valueToken := p.eat(TokenMultilineString)
    p.eat(TokenRBrace)
    return valueToken.Value.(string)
}

func (p *Parser) parseClassValue() map[string]interface{} {
    p.eat(TokenLBrace)
    obj := make(map[string]interface{})
    for p.currentToken().Type != TokenRBrace {
        name, value := p.parseParameter()
        obj[name] = value
    }
    p.eat(TokenRBrace)
    return obj
}

func (p *Parser) parseListValue() []interface{} {
    p.eat(TokenLParen)
    elementType := p.currentToken()

    var parserFunc func() interface{}

    switch elementType.Type {
    case TokenNum:
        p.eat(TokenNum)
        parserFunc = func() interface{} {
            return p.eat(TokenNumber).Value.(int)
        }
    case TokenFl:
        p.eat(TokenFl)
        parserFunc = func() interface{} {
            if p.currentToken().Type == TokenFloat {
                return p.eat(TokenFloat).Value.(float64)
            }
            return float64(p.eat(TokenNumber).Value.(int))
        }
    case TokenBool:
        p.eat(TokenBool)
        parserFunc = func() interface{} {
            return p.eat(TokenBoolean).Value.(bool)
        }
    case TokenStr:
        p.eat(TokenStr)
        parserFunc = func() interface{} {
            return p.eat(TokenString).Value.(string)
        }
    default:
        panic(newSyntaxError(fmt.Sprintf("Unsupported list element type: %s", elementType.Value), elementType.Line, elementType.Column))
    }

    p.eat(TokenRParen)
    p.eat(TokenLBrace)

    elements := make([]interface{}, 0)
    for p.currentToken().Type != TokenRBrace {
        elements = append(elements, parserFunc())
        if p.currentToken().Type == TokenComma {
            p.eat(TokenComma)
        } else if p.currentToken().Type != TokenRBrace {
            panic(newSyntaxError("Expected comma or closing brace", p.currentToken().Line, p.currentToken().Column))
        }
    }

    p.eat(TokenRBrace)
    return elements
}

func (p *Parser) parseDynamicValue() interface{} {
    p.eat(TokenLBrace)
    tok := p.currentToken()
    var val interface{}

    switch tok.Type {
    case TokenNumber:
        val = p.eat(TokenNumber).Value.(int)
    case TokenFloat:
        val = p.eat(TokenFloat).Value.(float64)
    case TokenBoolean:
        val = p.eat(TokenBoolean).Value.(bool)
    case TokenString:
        val = p.eat(TokenString).Value.(string)
    case TokenMultilineString:
        val = p.eat(TokenMultilineString).Value.(string)
    default:
        panic(newSyntaxError("dynamic supports only base types (bool, str, num, fl, ml)", tok.Line, tok.Column))
    }

    p.eat(TokenRBrace)
    return val
}