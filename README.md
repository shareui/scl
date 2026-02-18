<div align="center">
  <h1>SCL — Structured Configuration Language</h1>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

  A simple, human-readable configuration language with explicit typing and minimal syntax.
</div>

## What is SCL?

SCL is a configuration language built around explicit types and a clean, readable syntax. Every value declares its type, which makes configs predictable and easy to validate.

```
[ app config ]
name :: str { My App }
port :: num { 8080 }
debug :: bool { false }

database :: class {
  host :: str { localhost }
  port :: num { 5432 }
}

tags :: list[str] { "api", "backend" }
```

## Install

```bash
python -m pip install structcfg_parser-1.2.0-py3-none-any.whl
```
Or
```bash
curl -L -o structcfg_parser-1.2.0-py3-none-any.whl https://github.com/shareui/scl/releases/download/1.2.0/structcfg_parser-1.2.0-py3-none-any.whl && pip install structcfg_parser-1.2.0-py3-none-any.whl && rm structcfg_parser-1.2.0-py3-none-any.whl
```
## Documentation

Full language reference, API docs, and examples are in the [Python package README](python/README.md) and on [PyPI](https://pypi.org/project/structcfg-parser/).

Bug reports and feature requests go to [Issues](https://github.com/shareui/scl/issues).

## License

[MIT](LICENSE)

<div align="center">
  Made with ❤️ by <a href="https://t.me/shareui">shareui</a>
</div>
