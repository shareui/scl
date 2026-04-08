# scl-pip

Python package (`pyscl`) for [SCL](https://github.com/shareui/scl-c) — Structured Configuration Language.

Wraps the native C library via `ctypes`. No Python dependencies.

```sh
pip install pyscl
```

---

## Usage

```python
import scl

with scl.parseFile('config.scl') as doc:
    host = doc['server.host'].asString()
    port = doc.getPath('server.port').asInt()
```

```python
doc = scl.parse('@scl 1\nport: int = 8080\n')
print(doc['port'].asInt())     # 8080
print(doc.toJson())
```

---

## What SCL looks like

```scl
@scl 1

host: string = "localhost"
port: int @range(1, 65535) = 8080
tags: [string] = ["prod", "v2"]

db: struct {
    url: string
    pool: int
} = {
    url = "postgres://localhost/app"
    pool = 10
}
```

Every field has an explicit type. Invalid input is always a parse error.

---

## Platforms (Already compiled, you can compile it yourself)

| Platform | Architecture |
|---|---|
| Linux | x86_64 |
| Windows | x86_64 |
| Android | arm64-v8a |

Build from source for other targets: [shareui/scl-c](https://github.com/shareui/scl-c)

---

## Docs

- [Python API]()
- [Language reference](https://github.com/shareui/scl-c/blob/main/docs/scl-lang.md)
- [C ABI reference](https://github.com/shareui/scl-c/blob/main/docs/scl-abi.md)

## License

MIT
