from typing import Any, Dict, List

from .errors import SCLParseError


class Serializer:
    def __init__(self, indent: int = 4):
        self.indent = indent
    
    def serialize(self, data: Dict[str, Any], level: int = 0) -> str:
        lines: List[str] = []
        indent_str = " " * (self.indent * level)
        
        for key, value in data.items():
            line = f"{indent_str}{key} :: "
            
            if isinstance(value, bool):
                line += f"bool {{ {'true' if value else 'false'} }}"
            elif isinstance(value, int) and not isinstance(value, bool):
                line += f"num {{ {value} }}"
            elif isinstance(value, float):
                line += f"fl {{ {value} }}"
            elif isinstance(value, str):
                if '\n' in value:
                    line += f"ml {{\n{indent_str}    '{value}'\n{indent_str}}}"
                else:
                    escaped_str = value.replace('\\', '\\\\').replace('"', '\\"')
                    line += f'str {{ "{escaped_str}" }}'
            elif isinstance(value, dict):
                line += "class {\n"
                line += self.serialize(value, level + 1)
                line += f"{indent_str}}}"
            elif isinstance(value, list):
                if not value:
                    line += "list(str) { }"
                else:
                    first = value[0]
                    if isinstance(first, bool):
                        type_name = "bool"
                        if not all(isinstance(item, bool) for item in value):
                            raise SCLParseError(f"Mixed types in list for key '{key}': expected all bool")
                        items = ", ".join('true' if x else 'false' for x in value)
                    elif isinstance(first, int) and not isinstance(first, bool):
                        type_name = "num"
                        if not all(isinstance(item, int) and not isinstance(item, bool) for item in value):
                            raise SCLParseError(f"Mixed types in list for key '{key}': expected all int")
                        items = ", ".join(str(x) for x in value)
                    elif isinstance(first, float):
                        type_name = "fl"
                        valid_items = []
                        for item in value:
                            if isinstance(item, bool):
                                raise SCLParseError(f"Mixed types in list for key '{key}': bool not allowed in float list")
                            if not isinstance(item, (int, float)):
                                raise SCLParseError(f"Mixed types in list for key '{key}': expected all numeric")
                            valid_items.append(item)
                        items = ", ".join(str(x) if isinstance(x, float) else str(x) for x in valid_items)
                    elif isinstance(first, str):
                        type_name = "str"
                        if not all(isinstance(item, str) for item in value):
                            raise SCLParseError(f"Mixed types in list for key '{key}': expected all str")
                        escaped_items = [item.replace('\\', '\\\\').replace('"', '\\"') for item in value]
                        items = ", ".join(f'"{x}"' for x in escaped_items)
                    else:
                        raise SCLParseError(f"Unsupported list element type: {type(first)}")
                    line += f"list({type_name}) {{ {items} }}"
            else:
                line += self._serialize_dynamic(value)
            lines.append(line)
        return "\n".join(lines) + ("\n" if level == 0 else "\n")
    
    def _serialize_dynamic(self, value: Any) -> str:
        if isinstance(value, bool):
            return f"dynamic {{ {'true' if value else 'false'} }}"
        if isinstance(value, int) and not isinstance(value, bool):
            return f"dynamic {{ {value} }}"
        if isinstance(value, float):
            return f"dynamic {{ {value} }}"
        if isinstance(value, str):
            if '\n' in value:
                return f"ml {{\n    '{value}'\n}}"
            escaped_str = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'dynamic {{ "{escaped_str}" }}'
        raise SCLParseError(f"Unsupported value type: {type(value)}")


