from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Union, TYPE_CHECKING, Dict, Union, Set, List
from ast import Import, ImportFrom

from docoracle.blocks.link_block import LinkContext
from docoracle.discovery.paths import ModulePath
from docoracle.discovery.paths import ItemPath

if TYPE_CHECKING:
    from docoracle.discovery.paths import ModulePath
    from docoracle.blocks.items import FunctionBlock, ClassBlock
    from docoracle.blocks.assignments import AssignmentBlock


@dataclass
class PackageImportBlock:
    name: str
    alias: str
    package: str

    def to_path(self) -> ModulePath:
        return ModulePath(package=self.package, module=[])

    def link(
        self,
        item_context: Dict[ItemPath, Union[FunctionBlock, ClassBlock, AssignmentBlock]],
        link_context: LinkContext,
        imports: Dict[str, Union[ModuleImportBlock, PackageImportBlock]],
    ) -> Set[Union[ItemPath, ModulePath]]:
        """
        Attempt to link all items below the present hierarchy.

        If an item cannot be linked, return the path to the item to be searched.
        If an item cannot be linked, and there's no clues to where it came from,
        return all ModulePaths that are targeted with an import star.
        """
        return set()

    def is_linked(self) -> bool:
        return True


@dataclass
class ModuleImportBlock(PackageImportBlock):
    module: List[str]

    def to_path(self) -> ModulePath:
        return ModulePath(package=self.package, module=self.module)


def _split_module(term: str) -> Tuple[str, Optional[List[str]]]:
    terms = term.split(".")
    if len(terms) == 1:
        return terms, None
    return terms.pop(0), terms


def parse_import(
    item: Union[Import, ImportFrom], current_package: str, current_module: List[str]
) -> List[Union[PackageImportBlock, ModuleImportBlock]]:
    match item:
        case Import(_):
            res = []
            for alias in item.names:
                package, module = _split_module(alias.name)
                if module is not None:
                    res.append(
                        ModuleImportBlock(
                            package=package,
                            module=module,
                            alias=alias.asname,
                            name=alias.name,
                        )
                    )
                else:
                    res.append(
                        PackageImportBlock(
                            package=package, alias=alias.asname, name=alias.name
                        )
                    )
            return res

        case ImportFrom(_):
            if item.module is None:
                package = current_package
                module = current_module
            else:
                package, module = _split_module(item.module)
            return [
                ModuleImportBlock(
                    alias=alias.asname, package=package, module=module, name=alias.name
                )
                for alias in item.names
            ]
