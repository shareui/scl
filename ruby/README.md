# SCL (Ruby) — usage guide

This is a usage-focused guide. For the full SCL specification, see the root README.  
Full documentation: [click](https://gitlab.com/shareui/scl/-/blob/main/README.md?ref_type=heads)

## Installation

In your project directory:
```bash
gem build scl_parser.gemspec
gem install ./scl_parser-0.1.0.gem
```

Or add to Gemfile (after publishing):
```ruby
gem "scl_parser", "~> 0.1.0"
```

## Import and quick start

```ruby
require "scl_parser"

cfg = SCL.loads(%(
app :: class {
  name :: str { "Demo" }
  ports :: list(num) { 80, 443 }
  debug :: bool { true }
}
))

cfg_from_file = SCL.load("config.scl")

s = SCL.dumps(cfg)
SCL.dump(cfg, "out.scl")
```

## License

MIT


