from __future__ import annotations

from docoracle.discovery.paths import ItemPath, ModulePath

__all__ = ["Parameter", "Signature", "Parameter", "Signature"]

import logging

from dataclasses import dataclass
from typing import *
from docoracle.blocks.type_block import TypeBlock, UserDefinedType
from ast import (
    Attribute,
    Subscript,
    Constant,
    Name,
    Tuple as ast_Tuple,
    BinOp,
    List as ast_List,
    UnaryOp,
    USub,
)

if TYPE_CHECKING:
    from docoracle.blocks.module import ReferencedModules, ReferenceTable

LOGGER = logging.getLogger(__name__)


@dataclass
class LiteralType:
    value: Any


@dataclass
class BaseType:
    name: str
    type: Union[None, LiteralType, TypeBlock] = None

    def link(
        self,
        module: ModulePath,
        reference_table: ReferenceTable,
        referenced_modules: ReferencedModules,
    ):
        if self.type is None:
            item = ItemPath.from_module(module, item=self.name)
            while item in reference_table:
                item = reference_table[item]
            assert isinstance(item, ItemPath)
            block = referenced_modules[item.to_module()].fetch_item(item)
            self.type = UserDefinedType.from_item_path(item, block)

    def __hash__(self) -> int:
        return hash(tuple([self.name, self.type]))


@dataclass
class TypeSubScript:
    name: str
    inner: Union[BaseType, TypeSubScript, TypeList]
    type: Optional[TypeBlock] = None
    split: str = "."

    def link(
        self,
        module: ModulePath,
        reference_table: ReferenceTable,
        referenced_modules: ReferencedModules,
    ):
        item = ItemPath.from_module(module, item=self.name)
        while item in reference_table:
            item = reference_table[item]
        assert isinstance(item, ModulePath)
        self.type = item
        self.inner.link(module, reference_table, referenced_modules)

    @staticmethod
    def from_str(x: str):
        assert "." in x
        pre, post = tuple(x.split(".", 1))
        if pre == "Literal":
            return BaseType(name="Literal", type=LiteralType(post))
        return TypeSubScript(name=pre, inner=as_base_type(post))


@dataclass
class TypeList:
    """
    Type must be a container type, i.e. Union[T], List[T], Dict[K,V]
    """

    inner: Tuple[Union[BaseType, TypeSubScript, TypeList]]

    def link(
        self,
        module: ModulePath,
        reference_table: ReferenceTable,
        referenced_modules: ReferencedModules,
    ):
        for item in self.inner:
            if item is None:
                breakpoint()
            item.link(module, reference_table, referenced_modules)

    @staticmethod
    def from_str(x: str):
        assert "[" in x
        pre, post = tuple(x.split("[", 1))
        # Remove final ]
        post = post[:-1]
        TypeList(name=pre, inner=tuple([as_base_type(x) for x in post.split(",")]))


def as_base_type(x: str) -> Union[BaseType, TypeList, TypeSubScript]:
    dot_split = x.find(".")
    left_brace_split = x.find("[")
    if (dot_split == -1) and (left_brace_split == -1):
        return BaseType(x)
    elif (left_brace_split == -1) or dot_split < left_brace_split:
        return TypeSubScript.from_str(x)
    else:
        return TypeList.from_str(x)


def _collect_attribute(item: Union[Attribute, Name]) -> List[str]:
    match item:
        case Attribute(value, attr):
            return _collect_attribute(value) + [attr]
        case Name(id):
            return [id]


def retrieve_attribute_type(
    item: Tuple[UnaryOp, BinOp, Tuple, Constant, Attribute, Subscript, Name, str]
) -> Union[BaseType, TypeSubScript, TypeList]:
    match item:
        case str():
            return BaseType(name=item)
        case Name():
            return BaseType(name=item.id)
        case Constant():
            if item.value is None:
                return BaseType(name="None", type=TypeBlock(None))
            return BaseType(name=item.value)
        case Attribute():
            # Typically Attributes in types are Module Attributes, so I'm going to
            #   assume it's Attributes all the way down, i.e. x.Typing.Optional[t]
            return BaseType(name=".".join(_collect_attribute(item)))
        case Subscript():
            outer = retrieve_attribute_type(item.value)
            return TypeSubScript(outer.name, inner=retrieve_attribute_type(item.slice))
        case ast_Tuple():
            for i in item.elts:
                if i is None or retrieve_attribute_type(i) is None:
                    breakpoint()
            return TypeList(
                inner=tuple([retrieve_attribute_type(i) for i in item.elts])
            )
        case BinOp(left, _, right):
            return TypeList(
                inner=tuple(
                    [retrieve_attribute_type(left), retrieve_attribute_type(right)]
                )
            )
        case UnaryOp(op, operand):
            match op:
                case USub():
                    str_operand = "-"
                case _:
                    str_operand = ""
            return TypeSubScript(
                name=str_operand,
                inner=retrieve_attribute_type(operand),
                type=None,
                split=" ",
            )
        case ast_List(elts, ctx):
            return TypeList(inner=tuple([retrieve_attribute_type(x) for x in elts]))


class Parameter:
    """
    Parameters are the abstract, which can be abstracted into items.
    """

    name: str
    unevaluated_type: Union[None, BaseType, TypeSubScript, TypeList] = None
    type: Union[None, BaseType, TypeSubScript, TypeList] = None
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
            case BaseType() | TypeList() | TypeSubScript():
                self.unevaluated_type = unevaluated_type
            case Attribute() | Subscript() | Name() | str() | Constant() | BinOp():
                self.unevaluated_type = retrieve_attribute_type(unevaluated_type)
            case _:
                LOGGER.error(f"Received {unevaluated_type}")
                LOGGER.error(
                    f"Received unknown type {type(unevaluated_type)} - {unevaluated_type} in Parameter Init"
                )
                breakpoint()
                exit(-1)
        self.comment = comment

    def link(
        self,
        module: ModulePath,
        reference_table: ReferenceTable,
        referenced_modules: ReferencedModules,
    ):
        self.type = self.unevaluated_type
        # TODO: Treat 'self' differently
        if self.type is not None:
            self.type.link(module, reference_table, referenced_modules)


@dataclass
class Signature:
    parameters: List[Parameter]
    result: Union[None, BaseType, TypeSubScript, TypeList]

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

    def link(
        self,
        module: ModulePath,
        reference_table: ReferenceTable,
        referenced_modules: ReferencedModules,
    ):
        for item in self.parameters:
            item.link(module, reference_table, referenced_modules)
        if self.result is not None:
            self.result.link(module, reference_table, referenced_modules)
