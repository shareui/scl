package scl

import "fmt"

type ParseError struct {
    Message string
}

func (e *ParseError) Error() string {
    return e.Message
}

type SyntaxError struct {
    Message string
    Line    int
    Column  int
}

func (e *SyntaxError) Error() string {
    if e.Line > 0 && e.Column > 0 {
        return fmt.Sprintf("Syntax error at line %d, column %d: %s", e.Line, e.Column, e.Message)
    }
    return fmt.Sprintf("Syntax error: %s", e.Message)
}

func newSyntaxError(message string, line, column int) *SyntaxError {
    return &SyntaxError{
        Message: message,
        Line:    line,
        Column:  column,
    }
}