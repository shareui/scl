# SCL (Rust) — usage guide

This is a usage-focused guide. For the full SCL specification, see the root README.  
Full documentation: [click](https://gitlab.com/shareui/scl/-/blob/main/README.md?ref_type=heads)

## Installation

Add to your `Cargo.toml` (after publishing to crates.io) or use as a local path dependency.

```toml
[dependencies]
scl_parser = "0.1"
```

## Import and quick start

```rust
use std::collections::HashMap;
use scl_parser::{load, loads, dump, dumps, Value};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // From string
    let cfg = loads(r#"
app :: class {
  name :: str { "Demo" }
  debug :: bool { true }
  ports :: list(num) { 80, 443 }
}
"#)?;

    // Access
    if let Some(Value::Class(app)) = cfg.get("app") {
        if let Some(Value::Str(name)) = app.get("name") {
            println!("name = {}", name);
        }
    }

    // To string
    let s = dumps(&cfg, 4);
    println!("{}", s);

    // To file
    dump(&cfg, "out.scl", 4)?;
    Ok(())
}
```

## License

MIT


