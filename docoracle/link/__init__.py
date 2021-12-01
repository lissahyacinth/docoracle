import logging

from functools import lru_cache
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

from docoracle.blocks.type_block import TypeBlock, UnknownType, UserDefinedType

LOGGER = logging.getLogger(__name__)


@lru_cache
def try_link(type_block: TypeBlock) -> str:
    match type_block:
        case int():
            return "[int](https://docs.python.org/3/library/functions.html#int)"
        case float():
            return "[float](https://docs.python.org/3/library/functions.html#float)"
        case str():
            return "[str](https://docs.python.org/3/library/functions.html#str)"
        case bool():
            return "[str](https://docs.python.org/3/library/functions.html#bool)"
        case UnknownType(type_name):
            return f"{type_name}"
        case UserDefinedType(type_name):
            LOGGER.warning(f"Identifying UDT {type_name}")
        case _:
            return "A Type I'll fill in later"
