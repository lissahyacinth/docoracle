import sys
import logging
from typing import Union, Final


LOGGER = logging.getLogger(__name__)

PY_MINOR_VERSION: Final = sys.version_info[1]
import ast as ast3
from ast import (
    AST,
    Call,
    FunctionType,
    Name,
    Attribute,
    Ellipsis as ast3_Ellipsis,
    Starred,
    NameConstant,
    Expression as ast3_Expression,
    Str,
    Bytes,
    Index,
    Num,
    UnaryOp,
    USub,
)


def ast3_parse(
    source: Union[str, bytes],
    filename: str,
    mode: str,
    feature_version: int = PY_MINOR_VERSION,
) -> AST:
    return ast3.parse(
        source,
        filename,
        mode,
        type_comments=True,  # This works the magic
        feature_version=feature_version,
    )
