import pathlib
import functools

from operator import iconcat, xor
from typing import List, TypeVar, Optional, Any, Union

from docoracle.blocks.type_block import TypeBlock


T = TypeVar("T")


def str_coalesce(a: Optional[str], b: Optional[str]) -> Optional[str]:
    if a is not None and len(a.strip()) == 0:
        a = None
    if b is not None and len(b.strip()) == 0:
        b = None
    try:
        return coalesce(a, b)
    except ValueError:
        return None


def type_coalesce(a: Optional[TypeBlock], b: Optional[TypeBlock]) -> TypeBlock:
    if a.type is None:
        a = None
    if b.type is None:
        b = None
    try:
        return coalesce(a, b)
    except ValueError:
        return TypeBlock(None)


def coalesce(a: Optional[T], b: Optional[T]) -> T:
    match (a, b):
        case a, None:
            return a
        case None, b:
            return b
        case None, None:
            raise ValueError(f"Parameters a and b were both None")


def relative_module_path(loc: pathlib.Path, base_directory: pathlib.Path) -> List[str]:
    path = "/".join(
        filter(
            lambda x: len(x.strip()) > 0,
            str(loc)
            .replace(str(base_directory), "")
            .replace("__init__.py", "")
            .split("/"),
        )
    )
    if len(path) == 0:
        return "/"
    return path


def _combine(acc: List, x: Union[List, Any]) -> List:
    if isinstance(x, List):
        return iconcat(acc, x)
    else:
        return iconcat(acc, [x])


def flatten_list(x: List[List[Any]]) -> List[Any]:
    return functools.reduce(_combine, x, [])
