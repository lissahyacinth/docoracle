from __future__ import annotations

__all__ = ["Parameter", "Signature", "Parameter", "Signature"]

import logging

from dataclasses import dataclass
from typing import *
from docoracle.blocks.type_block import TypeBlock
from ast import Attribute, Subscript, Constant, Name, Tuple as ast_Tuple, BinOp

LOGGER = logging.getLogger(__name__)


@dataclass
class UnevaluatedBaseType:
    name: str


@dataclass
class UnevaluatedSubscript:
    name: str
    inner: Union[UnevaluatedBaseType, UnevaluatedSubscript, UnevaluatedList]


@dataclass
class UnevaluatedList:
    inner: List[Union[UnevaluatedBaseType, UnevaluatedSubscript, UnevaluatedList]]

def _collect_attribute(item: Union[Attribute, Name]) -> List[str]:
    match item:
        case Attribute(value, attr):
            return _collect_attribute(value) + [attr]
        case Name(id):
            return [id]

def retrieve_attribute_type(
    item: Tuple[BinOp, Tuple, Constant, Attribute, Subscript, Name, str]
) -> Union[UnevaluatedBaseType, UnevaluatedSubscript, UnevaluatedList]:
    match item:
        case str():
            return UnevaluatedBaseType(name=item)
        case Name():
            return UnevaluatedBaseType(name=item.id)
        case Constant():
            return UnevaluatedBaseType(name=item.value)
        case Attribute():
            # Typically Attributes in types are Module Attributes, so I'm going to 
            #   assume it's Attributes all the way down, i.e. x.Typing.Optional[t]
            return UnevaluatedBaseType(
                name='.'.join(_collect_attribute(item))
            )
        case Subscript():
            outer = retrieve_attribute_type(item.value)
            return UnevaluatedSubscript(
                outer.name, inner=retrieve_attribute_type(item.slice)
            )
        case ast_Tuple():
            return UnevaluatedList(
                inner=[retrieve_attribute_type(i) for i in item.elts]
            )
        case BinOp(left, _, right):
            return UnevaluatedList(
                inner=[retrieve_attribute_type(left), retrieve_attribute_type(right)]
            )


class Parameter:
    """
    Parameters are the abstract, which can be abstracted into items.
    """

    name: str
    unevaluated_type: Union[
        None, UnevaluatedBaseType, UnevaluatedSubscript, UnevaluatedList
    ] = None
    comment: Optional[str] = None

    def __init__(
        self,
        name: str,
        unevaluated_type: Union[str, Attribute, Subscript, None] = None,
        comment: Optional[str] = None,
    ) -> None:
        self.name = name
        match unevaluated_type:
            case None:
                self.unevaluated_type = None
            case UnevaluatedBaseType() | UnevaluatedList() | UnevaluatedSubscript():
                self.unevaluated_type = unevaluated_type
            case Attribute() | Subscript() | Name() | str() | Constant():
                self.unevaluated_type = retrieve_attribute_type(unevaluated_type)
            case _:
                LOGGER.error(f"Received {unevaluated_type}")
                LOGGER.error(
                    f"Received unknown type {type(unevaluated_type)} - {unevaluated_type} in Parameter Init"
                )
                breakpoint()
                exit(-1)
        self.comment = comment


@dataclass
class Signature:
    parameters: List[Parameter]
    result: Union[TypeBlock, str]

    def __hash__(self) -> int:
        return hash(tuple(self.parameters + [self.result]))

    def __str__(self) -> str:
        lhs = [
            f"{param.name} : {param.type if param.type is not None else param.unevaluated_type}"
            for param in self.parameters
        ]
        rhs = (
            f"{self.result.type if isinstance(self.result, TypeBlock) else self.result}"
        )
        return f"({', '.join(lhs)}) -> {rhs}"
