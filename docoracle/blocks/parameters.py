from __future__ import annotations

__all__ = ["Parameter", "Signature", "Parameter", "Signature"]

import logging

from dataclasses import dataclass
from typing import *
from docoracle.blocks.link_block import LinkContext
from docoracle.blocks.type_block import TypeBlock, UserDefinedType
from docoracle.discovery.paths import ItemPath, ModulePath
from ast import Attribute, Subscript, Constant, Name, Tuple as ast_Tuple

from docoracle.blocks.import_block import ModuleImportBlock, PackageImportBlock

if TYPE_CHECKING:
    from docoracle.blocks.items import FunctionBlock, ClassBlock
    from docoracle.blocks.module import ModuleBlock
    from docoracle.blocks.assignments import AssignmentBlock


LOGGER = logging.getLogger(__name__)


@dataclass
class UnevaluatedBaseType:
    prelim: str
    name: str


@dataclass
class UnevaluatedSubscript:
    prelim: str
    name: str
    inner: Union[UnevaluatedBaseType, UnevaluatedSubscript, UnevaluatedList]


@dataclass
class UnevaluatedList:
    inner: List[Union[UnevaluatedBaseType, UnevaluatedSubscript, UnevaluatedList]]


def retrieve_attribute_type(
    item: Tuple[Tuple, Constant, Attribute, Subscript, Name, str]
) -> Union[UnevaluatedBaseType, UnevaluatedSubscript, UnevaluatedList]:
    match item:
        case str():
            return UnevaluatedBaseType(prelim=None, name=item)
        case Name():
            return UnevaluatedBaseType(prelim=None, name=item.id)
        case Constant():
            return UnevaluatedBaseType(prelim=None, name=item.value)
        case Attribute():
            return UnevaluatedBaseType(
                name=getattr(item, "attr", None), prelim=getattr(item.value, "id")
            )
        case Subscript():
            outer = retrieve_attribute_type(item.value)
            return UnevaluatedSubscript(
                outer.prelim, outer.name, inner=retrieve_attribute_type(item.slice)
            )
        case ast_Tuple():
            return UnevaluatedList(
                inner=[retrieve_attribute_type(i) for i in item.elts]
            )


class Parameter:
    """
    Parameters are the abstract, which can be abstracted into items.
    """

    name: str
    unevaluated_type: Union[str, Attribute, Subscript, None] = None
    type: Optional[TypeBlock] = None
    comment: Optional[str] = None

    def __init__(
        self,
        name: str,
        unevaluated_type: Union[str, Attribute, Subscript, None] = None,
        type: Optional[TypeBlock] = None,
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
                exit(-1)
        self.type = type
        self.comment = comment

    def link(
        self,
        item_context: Dict[
            ItemPath, Union["FunctionBlock", "ClassBlock", "AssignmentBlock"]
        ],
        link_context: LinkContext,
        imports: Dict[str, Union[ModuleImportBlock, PackageImportBlock]],
    ) -> Set[Union[ItemPath, ModulePath]]:
        LOGGER.warning(f"Linking {self.name} with {self.unevaluated_type}")
        breakpoint()
        item_path = ItemPath(link_context.package, link_context.module, item_name)
        if item_path in item_context:
            target = item_context[item_name]
            self.type = TypeBlock(
                UserDefinedType(
                    package=link_context.package,
                    module=link_context.modulem,
                    item=str(target.__class__),
                    name=target.name,
                )
            )
            return set([])
        else:
            # TODO: Add relative import case
            if modules[0] in imports:
                target_package = imports[modules[0]]
                if "." in target_package:
                    split_package = target_package.split(".")
                    target_package = split_package[0]
                    target_modules = split_package[1:] + modules[1:]
                else:
                    target_modules = modules[1:]
                return set(
                    [
                        ItemPath(
                            package=target_package.name,
                            modules=target_modules,
                            item=item_name,
                        )
                    ]
                )
            else:
                return set(
                    module_import.to_path() for module_import in imports.values()
                )

    def is_linked(self) -> bool:
        return self.type is not None


@dataclass
class Signature:
    parameters: List[Parameter]
    result: Union[TypeBlock, str]

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
        item_context: Dict[
            ItemPath, Union["FunctionBlock", "ClassBlock", "AssignmentBlock"]
        ],
        package_context: Dict[ModulePath, Union[ModuleBlock, PackageImportBlock]],
        link_context: LinkContext,
    ) -> Set[Union[ItemPath, ModulePath]]:
        LOGGER.warning(f"Linking Signature for {self.parameters}")
        unlinked: Set[Union[ItemPath, ModulePath]] = set()
        for param in filter(lambda x: not x.is_linked(), self.parameters):
            unlinked = unlinked | param.link(
                item_context, package_context, link_context
            )
        return unlinked

    def is_linked(self) -> bool:
        return all([x.is_linked() for x in self.parameters]) and isinstance(
            self.result, TypeBlock
        )
