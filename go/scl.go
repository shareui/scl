// Package scl provides a parser and serializer for SCL (Structured Configuration Language).
package scl

import (
    "os"
)

const Version = "1.0.0"

// loads parses SCL text and returns a map representation.
func Loads(text string) (map[string]interface{}, error) {
    defer func() {
        if r := recover(); r != nil {
            if err, ok := r.(*SyntaxError); ok {
                panic(err)
            }
            panic(r)
        }
    }()

    lexer := NewLexer(text)
    tokens, err := lexer.Tokenize()
    if err != nil {
        return nil, err
    }

    parser := NewParser(tokens)
    return parser.Parse()
}

// load reads an SCL file and returns a map representation.
func Load(filename string) (map[string]interface{}, error) {
    data, err := os.ReadFile(filename)
    if err != nil {
        return nil, err
    }
    return Loads(string(data))
}

// dumps serializes a map to SCL format string.
func Dumps(data map[string]interface{}, indent int) (string, error) {
    if indent <= 0 {
        indent = 4
    }
    serializer := NewSerializer(indent)
    return serializer.Serialize(data)
}

// dump writes a map to an SCL file.
func Dump(data map[string]interface{}, filename string, indent int) error {
    if indent <= 0 {
        indent = 4
    }
    text, err := Dumps(data, indent)
    if err != nil {
        return err
    }
    return os.WriteFile(filename, []byte(text), 0644)
}