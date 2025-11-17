# SCL Parser for Go

A Go implementation of the SCL (Structured Configuration Language) parser.  
Full docs: [readme](https://github.com/shareui/scl/blob/main/README.md)  
Main repo: [scl](https://github.com/shareui/scl)

## Installation

```bash
go get github.com/shareui/scl-go
```

## Quick Start

```go
package main

import (
    "fmt"
    "log"
    
    scl "github.com/shareui/scl-go"
)

func main() {
    // From string
    config, err := scl.Loads(`
        app :: class {
            name :: str { "Demo" }
            debug :: bool { true }
            ports :: list(num) { 80, 443 }
            price :: fl { 19.99 }
        }
    `)
    if err != nil {
        log.Fatal(err)
    }
    
    app := config["app"].(map[string]interface{})
    fmt.Println(app["name"]) // "Demo"
    
    // From file
    fileConfig, err := scl.Load("config.scl")
    if err != nil {
        log.Fatal(err)
    }
    
    // To string
    output, err := scl.Dumps(config, 4)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(output)
    
    // To file
    err = scl.Dump(config, "output.scl", 4)
    if err != nil {
        log.Fatal(err)
    }
}
```

## API Reference

### `Loads(text string) (map[string]interface{}, error)`
Parse SCL text and return a map.

### `Load(filename string) (map[string]interface{}, error)`
Read and parse an SCL file.

### `Dumps(data map[string]interface{}, indent int) (string, error)`
Serialize a map to SCL format string.

### `Dump(data map[string]interface{}, filename string, indent int) error`
Write a map to an SCL file.

## Type Mapping

| SCL Type | Go Type |
|----------|---------|
| `bool` | `bool` |
| `str` | `string` |
| `num` | `int` |
| `fl` | `float64` |
| `ml` | `string` |
| `class` | `map[string]interface{}` |
| `list(T)` | `[]interface{}` |
| `dynamic` | `interface{}` |

## Example Configuration

```scl
database :: class {
    host :: str { "localhost" }
    port :: num { 5432 }
    ssl :: bool { true }
    timeout :: fl { 30.5 }
    
    credentials :: class {
        username :: str { "admin" }
        password :: str { "secret" }
    }
    
    replicas :: list(str) { "replica1", "replica2" }
}

features :: list(str) { "auth", "notifications" }
max_connections :: num { 100 }
debug :: bool { false }
```

## Complete Usage Example

```go
package main

import (
    "fmt"
    "log"
    
    scl "github.com/shareui/scl-go"
)

type Config struct {
    AppName     string
    Debug       bool
    Port        int
    DatabaseURL string
    Features    []string
}

func LoadConfig(filename string) (*Config, error) {
    raw, err := scl.Load(filename)
    if err != nil {
        return nil, fmt.Errorf("failed to load config: %w", err)
    }
    
    cfg := &Config{}
    
    if app, ok := raw["app"].(map[string]interface{}); ok {
        if name, ok := app["name"].(string); ok {
            cfg.AppName = name
        }
        if debug, ok := app["debug"].(bool); ok {
            cfg.Debug = debug
        }
        if port, ok := app["port"].(int); ok {
            cfg.Port = port
        }
    }
    
    if db, ok := raw["database"].(map[string]interface{}); ok {
        if url, ok := db["url"].(string); ok {
            cfg.DatabaseURL = url
        }
    }
    
    if features, ok := raw["features"].([]interface{}); ok {
        cfg.Features = make([]string, len(features))
        for i, f := range features {
            if str, ok := f.(string); ok {
                cfg.Features[i] = str
            }
        }
    }
    
    return cfg, nil
}

func main() {
    config, err := LoadConfig("config.scl")
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("App: %s\n", config.AppName)
    fmt.Printf("Debug: %v\n", config.Debug)
    fmt.Printf("Port: %d\n", config.Port)
    fmt.Printf("Features: %v\n", config.Features)
}
```

## Error Handling

The parser returns detailed syntax errors with line and column information:

```go
config, err := scl.Load("invalid.scl")
if err != nil {
    if syntaxErr, ok := err.(*scl.SyntaxError); ok {
        fmt.Printf("Syntax error at line %d, column %d: %s\n", 
            syntaxErr.Line, syntaxErr.Column, syntaxErr.Message)
    }
}
```

## License

MIT License

## Links

- Full SCL specification: https://github.com/shareui/scl