from __future__ import annotations


__all__ = ["TypeBlock"]


import logging

from enum import Enum
from typing import (
    TYPE_CHECKING,
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


from docoracle.discovery.paths import ItemPath

LOGGER = logging.getLogger(__name__)


@dataclass
class UserDefinedType(ItemPath):
    name: str


@dataclass
class UnknownType:
    name: str


@dataclass
class NoTypeSpecified:
    pass


@dataclass
class SelfType:
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
        NoTypeSpecified,
    ]

    @staticmethod
    def from_string(x: str) -> TypeBlock:
        match x:
            case "" | None:
                return TypeBlock(UnknownType)
            case "float":
                return TypeBlock(float)
            case "int":
                return TypeBlock(int)
            case "str":
                return TypeBlock(str)
            case "bool":
                return (TypeBlock(bool),)
            case "Sequence":
                return TypeBlock(Sequence)
            case _:
                return TypeBlock(UserDefinedType(x))
