# structcfg-parser

Python parser for [SCL (Structured Configuration Language)](https://github.com/shareui/scl) — a simple, human-readable configuration format with explicit typing.

```bash
pip install structcfg-parser
```

## Quick Start

```python
import scl_parser

config = scl_parser.loads("""
app :: class {
  name :: str { My Application }
  port :: num { 8080 }
  debug :: bool { true }
}
""")

print(config["app"]["name"])  # My Application
print(config["app"]["port"])  # 8080
```

---

## API

### Parsing

#### `loads(text: str) -> dict`

Parse SCL string to dict. Comments are not preserved.

```python
config = scl_parser.loads("count :: num { 42 }")
print(config["count"])  # 42
```

#### `load(filename: str, encoding: str = "utf-8") -> dict`

Load and parse SCL file to dict.

```python
config = scl_parser.load("config.scl")
```

#### `loadsWithComments(text: str) -> SCLDocument`

Parse SCL string to `SCLDocument`, preserving comments.

```python
doc = scl_parser.loadsWithComments("""
[ database settings ]
host :: str { localhost }  [ can be overridden via env ]
""")

print(doc["host"])                    # localhost
print(doc.getComment("host"))         # database settings
print(doc.getInlineComment("host"))   # can be overridden via env
```

#### `loadWithComments(filename: str, encoding: str = "utf-8") -> SCLDocument`

Load SCL file to `SCLDocument`.

```python
doc = scl_parser.loadWithComments("config.scl")
```

---

### Serialization

#### `dumps(data: dict | SCLDocument, indent: int = 4) -> str`

Serialize dict or `SCLDocument` to SCL string.

```python
config = {"host": "localhost", "port": 5432}
print(scl_parser.dumps(config))
# host :: str { "localhost" }
# port :: num { 5432 }
```

#### `dump(data: dict | SCLDocument, filename: str, indent: int = 4, encoding: str = "utf-8")`

Save dict or `SCLDocument` to file.

```python
scl_parser.dump(config, "output.scl")
```

#### `dumpsWithComments(doc: SCLDocument, indent: int = 4) -> str`

Serialize `SCLDocument` to SCL string with comments. Requires `SCLDocument` — use `dumps()` for plain dict.

#### `dumpWithComments(doc: SCLDocument, filename: str, indent: int = 4, encoding: str = "utf-8")`

Save `SCLDocument` to file with comments. Requires `SCLDocument`.

---

### SCLDocument

`SCLDocument` is returned by `loadsWithComments` / `loadWithComments`. It provides dict-like access to values and full control over comments.

```python
doc = scl_parser.loadsWithComments(text)

# dict-like access
doc["key"]
doc["key"] = value
del doc["key"]
"key" in doc
len(doc)

# explicit methods
doc.get("key", default=None)
doc.set("key", value, comment="...", inlineComment="...")
doc.delete("key")
doc.has("key")
doc.keys()
doc.values()
doc.items()

# comments
doc.getComment("key")           # comment before parameter
doc.getInlineComment("key")     # comment on the same line
doc.setComment("key", "...")
doc.setInlineComment("key", "...")
doc.getHeaderComment()          # comment at top of file
doc.setHeaderComment("...")

# conversion
doc.toDict()                    # plain dict, comments lost
SCLDocument.fromDict(d)         # create from dict, no comments
```

**Building a document from scratch:**

```python
doc = scl_parser.SCLDocument()
doc.setHeaderComment("generated config")
doc.set("host", "localhost", comment="database host")
doc.set("port", 5432, inlineComment="default postgres port")

print(scl_parser.dumpsWithComments(doc))
# [ generated config ]
#
# [ database host ]
# host :: str { "localhost" }
# port :: num { 5432 }  [ default postgres port ]
```

---

### Error Handling

```python
try:
    config = scl_parser.load("config.scl")
except FileNotFoundError:
    print("file not found")
except scl_parser.SCLSyntaxError as e:
    print(f"syntax error: {e}")
except scl_parser.SCLParseError as e:
    print(f"parse error: {e}")
```

---

## Language Reference

### Syntax

```
name :: type { value }
```

Comments use square brackets:

```
[ this is a comment ]
name :: str { hello }  [ inline comment ]
```

---

### Types

| Type | Description | Example |
|------|-------------|---------|
| `bool` | Boolean | `enabled :: bool { true }` |
| `str` | String | `name :: str { hello }` |
| `num` | Integer | `count :: num { 42 }` |
| `fl` | Float | `price :: fl { 19.99 }` |
| `ml` | Multiline string | `text :: ml { 'line1\nline2' }` |
| `class` | Object (key-value pairs) | `user :: class { ... }` |
| `list(T)` / `list[T]` | Typed list | `items :: list[num] { 1, 2, 3 }` |
| `dynamic` | Any scalar value | `value :: dynamic { 42 }` |

---

### `bool`

```
enabled :: bool { true }
flag :: bool { false }
active :: bool { yes }    [ yes/no are valid aliases ]
inactive :: bool { no }
```

---

### `str`

Values can be written with or without quotes. Quoted strings support escape sequences.

```
[ unquoted — literal text until } ]
greeting :: str { hello world }

[ quoted ]
path :: str { "C:\\Users\\admin" }
message :: str { "say \"hi\"" }
newline :: str { "line1\nline2" }
tab :: str { "col1\tcol2" }
unicode :: str { "\u041F\u0440\u0438\u0432\u0435\u0442" }
```

Supported escapes: `\\`, `\"`, `\'`, `\n`, `\t`, `\uXXXX`, any other `\x` → `x`.

---

### `num` / `fl`

```
count :: num { 42 }
negative :: num { -10 }
price :: fl { 19.99 }
ratio :: fl { 0.5 }
```

---

### `ml`

Multiline string. Value can be quoted with `'...'` or written plain.

```
[ quoted — supports escape sequences ]
body :: ml {
  'line one\nline two\ttabbed'
}

[ plain — literal text until } ]
note :: ml { some plain text }
```

---

### `class`

Nested object with any number of parameters. Nesting is unlimited.

```
server :: class {
  host :: str { localhost }
  port :: num { 8080 }
  tls :: bool { false }
}

org :: class {
  department :: class {
    team :: class {
      lead :: str { Alice }
    }
  }
}
```

---

### `list`

Strongly typed, homogeneous list. Type is specified in `()` or `[]` — both are accepted.

```
primes :: list(num) { 2, 3, 5, 7 }
tags :: list[str] { "alpha", "beta" }
flags :: list[bool] { true, false, true }
```

List of objects:

```
users :: list(class) {
  {
    name :: str { Alice }
    age :: num { 30 }
  },
  {
    name :: str { Bob }
    age :: num { 25 }
  }
}
```

Nested lists:

```
matrix :: list[list[num]] {
  { 1, 2, 3 },
  { 4, 5, 6 }
}
```

---

### `dynamic`

Any scalar value — type is inferred at runtime.

```
setting :: dynamic { 42 }
flag :: dynamic { true }
label :: dynamic { "hello" }
ratio :: dynamic { 3.14 }

mixed :: list(dynamic) { 1, "text", true, 3.14 }
```

---

## Links

- **SCL Specification**: [github.com/shareui/scl](https://github.com/shareui/scl)
- **Issues**: [github.com/shareui/scl/issues](https://github.com/shareui/scl/issues)
- **Author**: [shareui](https://t.me/shareui)
