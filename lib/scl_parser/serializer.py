from typing import Any, Dict, List, Union

from .errors import SCLParseError
from .document import SCLDocument


class Serializer:
    def __init__(self, indent: int = 4):
        self.indent = indent

    def serialize(self, data: Union[Dict[str, Any], SCLDocument], level: int = 0) -> str:
        if isinstance(data, SCLDocument):
            return self.serializeDocument(data)
        else:
            return self.serializeDict(data, level)

    def serializeDocument(self, doc: SCLDocument) -> str:
        lines: List[str] = []

        if doc.headerComment:
            lines.append(f"[ {doc.headerComment} ]")
            lines.append("")

        for key, value in doc.data.items():
            if key in doc.comments:
                lines.append(f"[ {doc.comments[key]} ]")

            line = f"{key} :: "
            line += self.serializeValue(value, 0)

            if key in doc.inlineComments:
                line += f"  [ {doc.inlineComments[key]} ]"

            lines.append(line)

        return "\n".join(lines) + "\n" if lines else ""

    def serializeDict(self, data: Dict[str, Any], level: int = 0) -> str:
        lines: List[str] = []
        indentStr = " " * (self.indent * level)

        for key, value in data.items():
            line = f"{indentStr}{key} :: "
            line += self.serializeValue(value, level)
            lines.append(line)

        return "\n".join(lines) + ("\n" if level == 0 else "\n")

    def serializeValue(self, value: Any, level: int = 0) -> str:
        indentStr = " " * (self.indent * level)

        if isinstance(value, bool):
            return f"bool {{ {'true' if value else 'false'} }}"
        elif isinstance(value, int) and not isinstance(value, bool):
            return f"num {{ {value} }}"
        elif isinstance(value, float):
            return f"fl {{ {value} }}"
        elif isinstance(value, str):
            if '\n' in value:
                return f"ml {{\n{indentStr}    '{value}'\n{indentStr}}}"
            else:
                escapedStr = value.replace('\\', '\\\\').replace('"', '\\"')
                return f'str {{ "{escapedStr}" }}'
        elif isinstance(value, dict):
            result = "class {\n"
            result += self.serializeDict(value, level + 1)
            result += f"{indentStr}}}"
            return result
        elif isinstance(value, list):
            return self.serializeList(value, level)
        else:
            return self.serializeDynamic(value, level)

    def getListType(self, lst: List[Any]) -> str:
        if not lst:
            return "list(str)"

        first = lst[0]

        if isinstance(first, list):
            innerType = self.getListType(first)
            return f"list({innerType})"
        elif isinstance(first, bool):
            return "list(bool)"
        elif isinstance(first, int) and not isinstance(first, bool):
            return "list(num)"
        elif isinstance(first, float):
            return "list(fl)"
        elif isinstance(first, str):
            return "list(ml)" if '\n' in first else "list(str)"
        elif isinstance(first, dict):
            return "list(class)"
        else:
            raise SCLParseError(f"Unsupported type: {type(first)}")

    def serializeList(self, value: List[Any], level: int) -> str:
        if not value:
            return "list(str) { }"

        listType = self.getListType(value)
        return self.serializeTypedList(value, listType, level)

    def serializeTypedList(self, value: List[Any], listType: str, level: int) -> str:
        if not value:
            return f"{listType} {{ }}"

        indentStr = " " * (self.indent * level)
        first = value[0]

        if not listType.startswith("list(") or not listType.endswith(")"):
            raise SCLParseError(f"Invalid list type: {listType}")

        innerType = listType[5:-1]

        if innerType == "bool":
            items = ", ".join('true' if x else 'false' for x in value)
            return f"{listType} {{ {items} }}"
        elif innerType == "num":
            items = ", ".join(str(x) for x in value)
            return f"{listType} {{ {items} }}"
        elif innerType == "fl":
            items = ", ".join(str(x) for x in value)
            return f"{listType} {{ {items} }}"
        elif innerType == "str":
            escapedItems = [x.replace('\\', '\\\\').replace('"', '\\"') for x in value]
            items = ", ".join(f'"{x}"' for x in escapedItems)
            return f"{listType} {{ {items} }}"
        elif innerType == "ml":
            result = f"{listType} {{\n"
            for i, item in enumerate(value):
                result += f"{indentStr}    '{item}'"
                if i < len(value) - 1:
                    result += ","
                result += "\n"
            result += f"{indentStr}}}"
            return result
        elif innerType == "class":
            result = f"{listType} {{\n"
            for i, item in enumerate(value):
                result += f"{indentStr}    {{\n"
                for key, val in item.items():
                    result += f"{indentStr}        {key} :: {self.serializeValue(val, level + 2)}\n"
                result += f"{indentStr}    }}"
                if i < len(value) - 1:
                    result += ","
                result += "\n"
            result += f"{indentStr}}}"
            return result
        elif innerType.startswith("list("):
            result = f"{listType} {{\n"
            for i, item in enumerate(value):
                innerSerialized = self.serializeTypedList(item, innerType, level + 1)
                innerContent = innerSerialized[len(innerType):].strip()
                result += f"{indentStr}    {innerContent}"
                if i < len(value) - 1:
                    result += ","
                result += "\n"
            result += f"{indentStr}}}"
            return result
        else:
            raise SCLParseError(f"Unknown inner type: {innerType}")

    def serializeDynamic(self, value: Any, level: int) -> str:
        if isinstance(value, bool):
            return f"dynamic {{ {'true' if value else 'false'} }}"
        if isinstance(value, int) and not isinstance(value, bool):
            return f"dynamic {{ {value} }}"
        if isinstance(value, float):
            return f"dynamic {{ {value} }}"
        if isinstance(value, str):
            if '\n' in value:
                return f"ml {{ '{value}' }}"
            escapedStr = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'dynamic {{ "{escapedStr}" }}'
        raise SCLParseError(f"Unsupported value type: {type(value)}")