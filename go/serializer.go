package scl

import (
    "fmt"
    "strings"
)

type Serializer struct {
    indent int
}

func NewSerializer(indent int) *Serializer {
    return &Serializer{indent: indent}
}

func (s *Serializer) Serialize(data map[string]interface{}) (string, error) {
    return s.serialize(data, 0), nil
}

func (s *Serializer) serialize(data map[string]interface{}, level int) string {
    lines := make([]string, 0)
    indentStr := strings.Repeat(" ", s.indent*level)

    for key, value := range data {
        line := fmt.Sprintf("%s%s :: ", indentStr, key)

        switch v := value.(type) {
        case bool:
            if v {
                line += "bool { true }"
            } else {
                line += "bool { false }"
            }
        case int:
            line += fmt.Sprintf("num { %d }", v)
        case float64:
            line += fmt.Sprintf("fl { %v }", v)
        case string:
            if strings.Contains(v, "\n") {
                line += fmt.Sprintf("ml {\n%s    '%s'\n%s}", indentStr, v, indentStr)
            } else {
                escaped := strings.ReplaceAll(v, "\\", "\\\\")
                escaped = strings.ReplaceAll(escaped, "\"", "\\\"")
                line += fmt.Sprintf("str { \"%s\" }", escaped)
            }
        case map[string]interface{}:
            line += "class {\n"
            line += s.serialize(v, level+1)
            line += fmt.Sprintf("%s}", indentStr)
        case []interface{}:
            if len(v) == 0 {
                line += "list(str) { }"
            } else {
                first := v[0]
                var typeName string
                var items []string

                switch first.(type) {
                case bool:
                    typeName = "bool"
                    for _, item := range v {
                        if b, ok := item.(bool); ok {
                            if b {
                                items = append(items, "true")
                            } else {
                                items = append(items, "false")
                            }
                        } else {
                            return fmt.Sprintf("Mixed types in list for key '%s': expected all bool", key)
                        }
                    }
                case int:
                    typeName = "num"
                    for _, item := range v {
                        if i, ok := item.(int); ok {
                            items = append(items, fmt.Sprintf("%d", i))
                        } else {
                            return fmt.Sprintf("Mixed types in list for key '%s': expected all int", key)
                        }
                    }
                case float64:
                    typeName = "fl"
                    for _, item := range v {
                        switch n := item.(type) {
                        case float64:
                            items = append(items, fmt.Sprintf("%v", n))
                        case int:
                            items = append(items, fmt.Sprintf("%d", n))
                        default:
                            return fmt.Sprintf("Mixed types in list for key '%s': expected all numeric", key)
                        }
                    }
                case string:
                    typeName = "str"
                    for _, item := range v {
                        if str, ok := item.(string); ok {
                            escaped := strings.ReplaceAll(str, "\\", "\\\\")
                            escaped = strings.ReplaceAll(escaped, "\"", "\\\"")
                            items = append(items, fmt.Sprintf("\"%s\"", escaped))
                        } else {
                            return fmt.Sprintf("Mixed types in list for key '%s': expected all str", key)
                        }
                    }
                default:
                    return fmt.Sprintf("Unsupported list element type: %T", first)
                }
                line += fmt.Sprintf("list(%s) { %s }", typeName, strings.Join(items, ", "))
            }
        default:
            line += s.serializeDynamic(v)
        }
        lines = append(lines, line)
    }

    result := strings.Join(lines, "\n")
    if level == 0 {
        result += "\n"
    } else {
        result += "\n"
    }
    return result
}

func (s *Serializer) serializeDynamic(value interface{}) string {
    switch v := value.(type) {
    case bool:
        if v {
            return "dynamic { true }"
        }
        return "dynamic { false }"
    case int:
        return fmt.Sprintf("dynamic { %d }", v)
    case float64:
        return fmt.Sprintf("dynamic { %v }", v)
    case string:
        if strings.Contains(v, "\n") {
            return fmt.Sprintf("ml {\n    '%s'\n}", v)
        }
        escaped := strings.ReplaceAll(v, "\\", "\\\\")
        escaped = strings.ReplaceAll(escaped, "\"", "\\\"")
        return fmt.Sprintf("dynamic { \"%s\" }", escaped)
    default:
        return fmt.Sprintf("Unsupported value type: %T", v)
    }
}