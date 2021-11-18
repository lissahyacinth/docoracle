from typing import TypeVar, Optional

from docoracle.blocks.type_block import TypeBlock


T = TypeVar('T')

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