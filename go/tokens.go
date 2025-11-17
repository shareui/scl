package scl

type TokenType int

const (
    TokenIdentifier TokenType = iota
    TokenDoubleColon
    TokenBool
    TokenStr
    TokenNum
    TokenFl
    TokenMl
    TokenClass
    TokenList
    TokenDynamic
    TokenLBrace
    TokenRBrace
    TokenLParen
    TokenRParen
    TokenComma
    TokenString
    TokenMultilineString
    TokenNumber
    TokenFloat
    TokenBoolean
    TokenComment
    TokenNewline
    TokenEOF
)

type Token struct {
    Type   TokenType
    Value  interface{}
    Line   int
    Column int
}

func (t TokenType) String() string {
    switch t {
    case TokenIdentifier:
        return "IDENTIFIER"
    case TokenDoubleColon:
        return "::"
    case TokenBool:
        return "bool"
    case TokenStr:
        return "str"
    case TokenNum:
        return "num"
    case TokenFl:
        return "fl"
    case TokenMl:
        return "ml"
    case TokenClass:
        return "class"
    case TokenList:
        return "list"
    case TokenDynamic:
        return "dynamic"
    case TokenLBrace:
        return "{"
    case TokenRBrace:
        return "}"
    case TokenLParen:
        return "("
    case TokenRParen:
        return ")"
    case TokenComma:
        return ","
    case TokenString:
        return "STRING"
    case TokenMultilineString:
        return "MULTILINE_STRING"
    case TokenNumber:
        return "NUMBER"
    case TokenFloat:
        return "FLOAT"
    case TokenBoolean:
        return "BOOLEAN"
    case TokenComment:
        return "COMMENT"
    case TokenNewline:
        return "NEWLINE"
    case TokenEOF:
        return "EOF"
    default:
        return "UNKNOWN"
    }
}