# SCL - Structured Configuration Language (C)

A C library for parsing and serializing SCL.
This is a usage-focused guide. For the full SCL specification, see the root README.  
Full documentation: [click](https://gitlab.com/shareui/scl/-/blob/main/README.md?ref_type=heads)

Supported features:
- bool, str, num, fl, ml
- class (dictionary object with arbitrary number of fields)
- list(type) for base types (bool/str/num/fl)
- dynamic: base types only (bool/str/num/fl/ml), without list/class

## Structure

- `include/scl_parser.h` — public API
- `src/scl_lexer.c` — lexer
- `src/scl_parser.c` — parser and serialization
- `src/scl_value.c` — value type and memory management

## SCL (C) — usage guide

This is a usage-focused guide. For the full SCL specification, see the root README.
Full documentation (placeholder link, replace later): https://gitlab.com/shareui/scl

## Integration into your project (without Make/CMake)

- Add `include/scl_parser.h` to your project's include path.
- Add source files `src/scl_value.c`, `src/scl_lexer.c`, `src/scl_parser.c` to your project build.
- Compile together with the rest of your project files (no separate makefiles required).

## Usage

```c
#include "scl_parser.h"
#include <stdio.h>

int main() {
	const char *text =
		"anyname :: class {\n"
		"  height :: num { 200 }\n"
		"  width :: num { 1000 }\n"
		"}\n";
	scl_value_t *cfg = NULL;
	char *err = NULL;
	if (scl_loads(text, &cfg, &err) != 0) {
		fprintf(stderr, "ERR: %s\n", err);
		scl_free_error(err);
		return 1;
	}
	char *out = scl_dumps(cfg, 4, NULL);
	puts(out);
	free(out);
	scl_free(cfg);
	return 0;
}
```

## License

MIT