<div align="center">
  <h1>SCL — Structured Configuration Language</h1>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  
  A simple, human-readable configuration language with explicit typing and minimal syntax.
</div>

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Language Guide](#language-guide)
  - [Basic Syntax](#basic-syntax)
  - [Supported Types](#supported-types)
  - [Advanced Features](#advanced-features)
- [Language Implementations](#language-implementations)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Simple Syntax** - Clean and minimal syntax for configuration
- **Type Safety** - Strong, explicit typing system
- **Extensible** - Support for nested objects and custom types
- **Cross-Platform** - Multiple language implementations
- **Human-Readable** - Designed to be both machine and human friendly

## Quick Start

1. **Install** the appropriate library for your language:
   ```bash
   # Python
   pip install structcfg-parser==1.1.0
   
   # Elixir (not published)
   def deps do
     [{:scl_parser, "~> 0.1.0"}]
   end
   
   # Ruby (not published)
   gem install scl_parser

   ```

2. **Create** a configuration file (e.g., `config.scl`):
   ```scl
   app :: class {
     name :: str { "My App" }
     version :: str { "1.0.0" }
     debug :: bool { true }
     
     server :: class {
       host :: str { "0.0.0.0" }
       port :: num { 3000 }
       environment :: str { "development" }
     }
     
     features :: list(str) { "auth", "notifications", "analytics" }
   }
   ```

3. **Use** it in your code:
   ```python
   # Python
   import scl_parser
   config = scl_parser.load("config.scl")
   print(config["app"]["name"])  # "My App"
   ```

## Language Guide

### Basic Syntax

SCL follows a simple pattern:

```scl
parameter_name :: type { value }
```

Comments are enclosed in square brackets:
```scl
[ This is a comment ]
name :: str { "John" }  [ This is also a comment ]
```

### Supported Types

## Basic Syntax

```
param_name :: type { value }
```

Comments:
```
[ Comment ]
```

Whitespace and blank lines are ignored.

### Supported Types

SCL supports the following data types:

| Type     | Description                                      | Example                           |
|----------|--------------------------------------------------|-----------------------------------|
| `bool`   | Boolean values                                   | `true`, `false`, `yes`, `no`     |
| `str`    | String with escapes (`\"`, `\\`, `\n`, `\t`)  | `"Hello \"World\""`           |
| `num`    | Integer (signed)                                 | `42`, `-10`, `0`                 |
| `fl`     | Floating-point number                            | `3.14`, `-0.5e10`, `100.0`       |
| `ml`     | Multiline string (single-quoted block)           | `'Line 1\nLine 2'`             |
| `class`  | Object (key-value pairs)                         | `{ key :: str { "value" } }`     |
| `list(T)`| Homogeneous list of type T                       | `list(str) { "a", "b" }`        |
| `dynamic`| Any scalar value (bool/str/num/fl)               | `dynamic { 42 }`                 |

### Type Examples

Here are examples of each type in action:

```
enabled :: bool { true }
title :: str { "Hello \"World\"" }
count :: num { -10 }
price :: fl { 19.99 }
description :: ml {
  'Multiline
  text'
}

user :: class {
  name :: str { "John" }
  age :: num { 30 }
  active :: bool { yes }
}

numbers :: list(num) { 1, 2, 3 }
names :: list(str) { "Alice", "Bob" }
flags :: list(bool) { true, false }
prices :: list(fl) { 9.99, 19.99, 29.0 }

object :: dynamic { 1 }
flag :: dynamic { true }
dyn_title :: dynamic { "hello" }
mltext :: dynamic {
  'multiline ok'
}
```}

## Advanced Features

### Nested Objects

SCL supports unlimited nesting of objects. Here's an example of a complex configuration:

```scl
database :: class {
  production :: class {
    host :: str { "db-prod.example.com" }
    port :: num { 5432 }
    credentials :: class {
      username :: str { "admin" }
      password :: str { "s3cr3t" }
    }
  }
  
  development :: class {
    host :: str { "localhost" }
    port :: num { 5432 }
    credentials :: class {
      username :: str { "dev" }
      password :: str { "devpass" }
    }
  }
}
```

### Lists and Collections

SCL supports strongly-typed lists:

```scl
# List of numbers
primes :: list(num) { 2, 3, 5, 7, 11, 13 }

# List of objects
users :: list(class) {
  {
    id :: num { 1 }
    name :: str { "Alice" }
    roles :: list(str) { "admin", "user" }
  },
  {
    id :: num { 2 }
    name :: str { "Bob" }
    roles :: list(str) { "user" }
  }
}
```

### Dynamic Values

For flexibility, use `dynamic` type:

```scl
# These are all valid dynamic values
setting1 :: dynamic { 42 }          # Number
setting2 :: dynamic { "value" }     # String
setting3 :: dynamic { true }        # Boolean
setting4 :: dynamic { 3.14 }        # Float

# Dynamic values can be used in classes
config :: class {
  timeout :: dynamic { 30 }         # Could be used as number
  feature_flag :: dynamic { true }  # Or as boolean
}
```

### String Escapes and Multiline Strings

```scl
# Basic string with escapes
escaped :: str { "Line 1\nLine 2\tTab\"Quote\\Backslash" }

# Multiline strings preserve formatting
multiline :: ml {
  'This is a multiline
  string that preserves
  indentation and line breaks.'
}
```

## Language Implementations

### SCL is available in multiple programming languages:

#### Python
• Ready  
• Stable  
• Available on PIP `structcfg-parser==1.1.0`  

#### Kotlin/Java
• Not ready  

#### Elixir
• Ready  
• Tested  
• Not available on mix  

#### Ruby
• Ready  
• Tested  
• Not available on gem  

#### C
• Ready  
• Not tested  
• Available from src  

#### Rust
• Ready  
• Not tested  
• Not available on cargo  

#### Go 
• Ready  
• Not tested  
• Aviable from `go get`
• Repository: [click](https://github.com/shareui/scl-go)

#### JavaScript/TypeScript
• Not ready  

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - File an issue with detailed reproduction steps
2. **Suggest features** - Open an issue to discuss new ideas
3. **Submit PRs** - Follow these steps:
   - Fork the repository
   - Create a feature branch
   - Add tests for your changes
   - Submit a pull request

## License

SCL is open source software licensed under the [MIT License](LICENSE).

## Acknowledgements
- Inspired by TOML, JSON, and other configuration formats
- Created and maintained by [shareui](https://t.me/shareui)

<div align="center">
  Made with ❤️ by <a href="https://t.me/shareui">shareui</a>
</div>


