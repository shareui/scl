# SCL (Python) — usage guide

This is a usage-focused guide. For the full SCL specification, see the root README.  
Full documentation: [click](https://gitlab.com/shareui/scl/-/blob/main/README.md?ref_type=heads)

## Installation

```bash
pip install structcfg-parser
```

Or in `requirements.txt`:
```
structcfg-parser==1.1.0
```

## Import and quick start

```python
import scl_parser

# From file
config = scl_parser.load("config.scl")

# From string
config = scl_parser.loads("count :: num { 42 }")

# To file
scl_parser.dump(config, "output.scl")

# To string
s = scl_parser.dumps(config)
```

## Examples

```python
import scl_parser

cfg = scl_parser.loads("""
app :: class {
  name :: str { "Demo" }
  debug :: bool { true }
  ports :: list(num) { 80, 443 }
  price :: fl { 19.99 }
  note :: ml {
    'hello
    world'
  }
}
""")
print(cfg["app"]["name"]) # app <- this is class
# name <- this is a parameter

file_cfg = scl_parser.load("path/to/config.scl")

param = file_cfg["class"]["param"]
only_param = file_cfg["param2"] # param with no class

```

## Configuration loading example
`config.py` file from the repository: [gitstats](https://github.com/shareui/GitLab-statistic)
```python
import logging
import scl_parser

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.telegram_bot_token = None
        self.target_channel_id = None
        self.gitlab_private_token = None
        self.target_gitlab_username = None
        self.schedule_interval_hours = None
        self.health_check_port = None
        self.max_displayed_languages = None
        self.quote = None
        self.force_message_id = None
        self.max_file_lines = None
        self.language_map = {}
    
    @classmethod
    def load(cls):
        try:
            raw_config = scl_parser.load("scl/config.scl")
        except FileNotFoundError:
            logger.error("Configuration file 'scl/config.scl' not found!")
            raise
        except scl_parser.SCLSyntaxError as e:
            logger.error(f"Configuration syntax error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
        
        config = cls()
        config.telegram_bot_token = raw_config['telegram']['bot_token']
        config.target_channel_id = raw_config['telegram']['target_channel_id']
        config.gitlab_private_token = raw_config['gitlab']['private_token']
        config.target_gitlab_username = raw_config['gitlab']['target_username']
        config.schedule_interval_hours = raw_config['scheduler']['interval_hours']
        config.health_check_port = raw_config['health_check']['port']
        config.max_displayed_languages = raw_config['display']['max_displayed_languages']
        config.quote = raw_config['display']['quote']
        config.force_message_id = raw_config['display']['force_message_id']
        config.max_file_lines = raw_config['limits']['max_file_lines']
        
        for ext, lang in raw_config['language_map'].items():
            config.language_map[f'.{ext}'] = lang
        
        return config
```

## License

MIT License
