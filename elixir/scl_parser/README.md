# SCL (Elixir) — usage guide

This is a usage-focused guide. For the full SCL specification, see the root README.  
Full documentation: [click](https://gitlab.com/shareui/scl/-/blob/main/README.md?ref_type=heads)

## Installation

Add dependency to `mix.exs`:
```elixir
def deps do
  [
    {:scl_parser, "~> 0.1.0"}
  ]
end
```

## Import and quick start

```elixir
alias SCL

cfg = SCL.loads("""
app :: class {
  name :: str { "Demo" }
  ports :: list(num) { 80, 443 }
  debug :: bool { true }
}
""")

cfg_from_file = SCL.load("config.scl")

s = SCL.dumps(cfg)
:ok = SCL.dump(cfg, "out.scl")
```

## License

MIT


