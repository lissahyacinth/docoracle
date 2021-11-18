from __future__ import annotations

__all__ = ["TypeBlock"]


from enum import Enum
from typing import (
    Sequence,
    Tuple,
    List,
    Set,
    Union,
    Callable,
    Iterator,
    Dict,
)
from dataclasses import dataclass

@dataclass
class UserDefinedType:
    name: str


@dataclass
class UnknownType:
    name: str


@dataclass
class NoTypeSpecified:
    pass


@dataclass
class TypeBlock:
    type: Union[
        None,
        Dict[TypeBlock, TypeBlock],
        Set,
        List[TypeBlock],
        Tuple,
        int,
        float,
        complex,
        str,
        bool,
        Iterator[TypeBlock],
        Sequence,
        bytes,
        Callable,
        UserDefinedType,
        Enum,
        UnknownType,
        NoTypeSpecified
    ]

    @staticmethod
    def from_string(x: str) -> TypeBlock:
        match x:
            case '' | None:
                return TypeBlock(UnknownType)
            case 'float':
                return TypeBlock(float)
            case 'int':
                return TypeBlock(int)
            case _:
                return TypeBlock(UserDefinedType(x))

    def try_link(self) -> str:
        match self.type:
            case int():
                return "[int](https://docs.python.org/3/library/functions.html#int)"
            case float():
                return "[float](https://docs.python.org/3/library/functions.html#float)"
            case str():
                return "[str](https://docs.python.org/3/library/functions.html#str)"
            case UnknownType(type_name):
                return f"{type_name}"
            case _:
                return "A Type I'll fill in later"