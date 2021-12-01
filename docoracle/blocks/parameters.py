from __future__ import annotations

__all__ = ["Parameter", "Signature", "Parameter", "Signature"]

from dataclasses import dataclass
from typing import *
from docoracle.blocks.link_block import LinkContext
from docoracle.blocks.type_block import TypeBlock, UserDefinedType
from docoracle.discovery.paths import ItemPath, ModulePath


from docoracle.blocks.import_block import ImportBlock, ModuleImportBlock

if TYPE_CHECKING:
    from docoracle.blocks.items import FunctionBlock, ClassBlock
    from docoracle.blocks.module import ModuleBlock
    from docoracle.blocks.assignments import AssignmentBlock


@dataclass
class Parameter:
    """
    Parameters are the abstract, which can be abstracted into items.
    """

    name: str
    string_type: Optional[str] = None
    type: Optional[TypeBlock] = None
    comment: Optional[str] = None

    def link(
        self,
        item_context: Dict[
            ItemPath, Union["FunctionBlock", "ClassBlock", "AssignmentBlock"]
        ],
        link_context: LinkContext,
        imports: Dict[str, Union[ImportBlock, ModuleImportBlock]],
    ) -> Set[Union[ItemPath, ModulePath]]:
        split_string = self.string_type.split()
        if len(split_string) > 1:
            modules, item_name = split_string[:-1], split_string[-1]
        else:
            modules = []
            item_name = split_string[0]
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
        lhs = [f"{param.name} : {param.type}" for param in self.parameters]
        rhs = (
            f"{self.result.type if isinstance(self.result, TypeBlock) else self.result}"
        )
        return f"({', '.join(lhs)}) -> {rhs}"

    def link(
        self,
        item_context: Dict[
            ItemPath, Union["FunctionBlock", "ClassBlock", "AssignmentBlock"]
        ],
        package_context: Dict[ModulePath, Union[ModuleBlock, ModuleImportBlock]],
        link_context: LinkContext,
    ) -> Set[Union[ItemPath, ModulePath]]:
        unlinked: Set[Union[ItemPath, ModulePath]] = set()
        for param in filter(lambda x: not x.is_linked, self.parameters):
            unlinked = unlinked | param.link(item_context, package_context, link_context)
        return unlinked

    def is_linked(self) -> bool:
        return all([x.is_linked() for x in self.parameters]) and isinstance(
            self.result, TypeBlock
        )
