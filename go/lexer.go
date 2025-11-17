package scl

import (
    "strconv"
    "strings"
    "unicode"
)

type Lexer struct {
    text   string
    pos    int
    line   int
    column int
    tokens []Token
}

func NewLexer(text string) *Lexer {
    return &Lexer{
        text:   text,
        pos:    0,
        line:   1,
        column: 1,
        tokens: make([]Token, 0),
    }
}

func (l *Lexer) peek(offset int) rune {
    pos := l.pos + offset
    if pos < len(l.text) {
        return rune(l.text[pos])
    }
    return 0
}

func (l *Lexer) advance() rune {
    if l.pos < len(l.text) {
        char := rune(l.text[l.pos])
        l.pos++
        if char == '\n' {
            l.line++
            l.column = 1
        } else {
            l.column++
        }
        return char
    }
    return 0
}

func (l *Lexer) skipWhitespace() {
    for l.peek(0) == ' ' || l.peek(0) == '\t' {
        l.advance()
    }
}

func (l *Lexer) readComment() Token {
    startLine := l.line
    startCol := l.column
    l.advance()
    var comment strings.Builder
    for l.peek(0) != 0 && l.peek(0) != ']' {
        comment.WriteRune(l.advance())
    }
    if l.peek(0) != ']' {
        panic(newSyntaxError("Unclosed comment", l.line, l.column))
    }
    l.advance()
    return Token{Type: TokenComment, Value: strings.TrimSpace(comment.String()), Line: startLine, Column: startCol}
}

func (l *Lexer) readString() Token {
    startLine := l.line
    startCol := l.column
    l.advance()
    var str strings.Builder
    for l.peek(0) != 0 && l.peek(0) != '"' {
        if l.peek(0) == '\\' {
            l.advance()
            nextChar := l.peek(0)
            if nextChar == 0 {
                panic(newSyntaxError("Unexpected end of string after backslash", l.line, l.column))
            }
            switch nextChar {
            case 'n':
                str.WriteRune('\n')
            case 't':
                str.WriteRune('\t')
            case '"', '\\':
                str.WriteRune(nextChar)
            default:
                str.WriteRune(nextChar)
            }
            l.advance()
        } else {
            str.WriteRune(l.advance())
        }
    }
    if l.peek(0) != '"' {
        panic(newSyntaxError("Unclosed string", l.line, l.column))
    }
    l.advance()
    return Token{Type: TokenString, Value: str.String(), Line: startLine, Column: startCol}
}

func (l *Lexer) readMultilineString() Token {
    startLine := l.line
    startCol := l.column
    l.advance()
    var str strings.Builder
    for l.peek(0) != 0 && l.peek(0) != '\'' {
        str.WriteRune(l.advance())
    }
    if l.peek(0) != '\'' {
        panic(newSyntaxError("Unclosed multiline string", l.line, l.column))
    }
    l.advance()
    return Token{Type: TokenMultilineString, Value: str.String(), Line: startLine, Column: startCol}
}

func (l *Lexer) readNumber() Token {
    startLine := l.line
    startCol := l.column
    var num strings.Builder

    if l.peek(0) == '-' {
        num.WriteRune(l.advance())
        if l.peek(0) == 0 || !unicode.IsDigit(l.peek(0)) {
            panic(newSyntaxError("Expected digit after '-'", l.line, l.column))
        }
    }

    hasDot := false
    for l.peek(0) != 0 && (unicode.IsDigit(l.peek(0)) || l.peek(0) == '.') {
        if l.peek(0) == '.' {
            if hasDot {
                break
            }
            hasDot = true
        }
        num.WriteRune(l.advance())
    }

    numStr := num.String()
    if hasDot {
        val, err := strconv.ParseFloat(numStr, 64)
        if err != nil {
            panic(newSyntaxError("Invalid float format", startLine, startCol))
        }
        return Token{Type: TokenFloat, Value: val, Line: startLine, Column: startCol}
    }
    val, err := strconv.ParseInt(numStr, 10, 64)
    if err != nil {
        panic(newSyntaxError("Invalid number format", startLine, startCol))
    }
    return Token{Type: TokenNumber, Value: int(val), Line: startLine, Column: startCol}
}

func (l *Lexer) readIdentifier() Token {
    startLine := l.line
    startCol := l.column
    var ident strings.Builder
    for l.peek(0) != 0 && (unicode.IsLetter(l.peek(0)) || unicode.IsDigit(l.peek(0)) || l.peek(0) == '_' || l.peek(0) == '-') {
        ident.WriteRune(l.advance())
    }

    identStr := ident.String()
    keywords := map[string]TokenType{
        "bool":    TokenBool,
        "str":     TokenStr,
        "num":     TokenNum,
        "fl":      TokenFl,
        "ml":      TokenMl,
        "class":   TokenClass,
        "list":    TokenList,
        "dynamic": TokenDynamic,
    }
    booleans := map[string]bool{
        "true":  true,
        "false": false,
        "yes":   true,
        "no":    false,
    }

    if tokType, ok := keywords[identStr]; ok {
        return Token{Type: tokType, Value: identStr, Line: startLine, Column: startCol}
    }
    if boolVal, ok := booleans[identStr]; ok {
        return Token{Type: TokenBoolean, Value: boolVal, Line: startLine, Column: startCol}
    }
    return Token{Type: TokenIdentifier, Value: identStr, Line: startLine, Column: startCol}
}

func (l *Lexer) Tokenize() ([]Token, error) {
    defer func() {
        if r := recover(); r != nil {
            if err, ok := r.(*SyntaxError); ok {
                panic(err)
            }
            panic(r)
        }
    }()

    for l.pos < len(l.text) {
        l.skipWhitespace()
        if l.peek(0) == 0 {
            break
        }

        if l.peek(0) == '[' {
            l.tokens = append(l.tokens, l.readComment())
            continue
        }

        if l.peek(0) == '\n' {
            line := l.line
            col := l.column
            l.advance()
            l.tokens = append(l.tokens, Token{Type: TokenNewline, Value: "\n", Line: line, Column: col})
            continue
        }

        if l.peek(0) == ':' && l.peek(1) == ':' {
            col := l.column
            l.advance()
            l.advance()
            l.tokens = append(l.tokens, Token{Type: TokenDoubleColon, Value: "::", Line: l.line, Column: col})
            continue
        }

        singles := map[rune]TokenType{
            '{': TokenLBrace,
            '}': TokenRBrace,
            '(': TokenLParen,
            ')': TokenRParen,
            ',': TokenComma,
        }
        if tokType, ok := singles[l.peek(0)]; ok {
            col := l.column
            ch := l.advance()
            l.tokens = append(l.tokens, Token{Type: tokType, Value: string(ch), Line: l.line, Column: col})
            continue
        }

        if l.peek(0) == '"' {
            l.tokens = append(l.tokens, l.readString())
            continue
        }

        if l.peek(0) == '\'' {
            l.tokens = append(l.tokens, l.readMultilineString())
            continue
        }

        if l.peek(0) == '-' && unicode.IsDigit(l.peek(1)) {
            l.tokens = append(l.tokens, l.readNumber())
            continue
        }

        if unicode.IsDigit(l.peek(0)) {
            peekAhead := l.pos + 1
            for peekAhead < len(l.text) && unicode.IsDigit(rune(l.text[peekAhead])) {
                peekAhead++
            }
            if peekAhead < len(l.text) && (unicode.IsLetter(rune(l.text[peekAhead])) || l.text[peekAhead] == '_') {
                l.tokens = append(l.tokens, l.readIdentifier())
            } else {
                l.tokens = append(l.tokens, l.readNumber())
            }
            continue
        }

        if unicode.IsLetter(l.peek(0)) || l.peek(0) == '_' {
            l.tokens = append(l.tokens, l.readIdentifier())
            continue
        }

        panic(newSyntaxError("Unexpected character: "+string(l.peek(0)), l.line, l.column))
    }

    l.tokens = append(l.tokens, Token{Type: TokenEOF, Value: nil, Line: l.line, Column: l.column})
    return l.tokens, nil
}