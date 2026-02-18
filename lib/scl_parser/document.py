from typing import Any, Dict, List, Optional, Union


class SCLDocument:
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.comments: Dict[str, str] = {}
        self.inlineComments: Dict[str, str] = {}
        self.headerComment: Optional[str] = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any, comment: Optional[str] = None, inlineComment: Optional[str] = None):
        self.data[key] = value
        if comment:
            self.comments[key] = comment
        if inlineComment:
            self.inlineComments[key] = inlineComment

    def delete(self, key: str):
        if key in self.data:
            del self.data[key]
        if key in self.comments:
            del self.comments[key]
        if key in self.inlineComments:
            del self.inlineComments[key]

    def has(self, key: str) -> bool:
        return key in self.data

    def keys(self) -> List[str]:
        return list(self.data.keys())

    def values(self) -> List[Any]:
        return list(self.data.values())

    def items(self):
        return self.data.items()

    def getComment(self, key: str) -> Optional[str]:
        return self.comments.get(key)

    def getInlineComment(self, key: str) -> Optional[str]:
        return self.inlineComments.get(key)

    def setComment(self, key: str, comment: str):
        self.comments[key] = comment

    def setInlineComment(self, key: str, comment: str):
        self.inlineComments[key] = comment

    def setHeaderComment(self, comment: str):
        self.headerComment = comment

    def getHeaderComment(self) -> Optional[str]:
        return self.headerComment

    def toDict(self) -> Dict[str, Any]:
        return self.data.copy()

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> 'SCLDocument':
        doc = cls()
        doc.data = data.copy()
        return doc

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value

    def __delitem__(self, key: str):
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"SCLDocument({len(self.data)} keys)"