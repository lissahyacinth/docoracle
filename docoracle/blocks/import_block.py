from __future__ import annotations

from dataclasses import dataclass
from os import name
from typing import Optional, Tuple, Union, TYPE_CHECKING, Dict, Union, List
from ast import Import, ImportFrom

from docoracle.discovery.paths import ItemPath, ModulePath, find_resource_path

if TYPE_CHECKING:
    from docoracle.discovery.paths import ModulePath


@dataclass
class Aliases:
    items: Dict[str, str]

    def get(self, id: str) -> Optional[ModulePath]:
        return self.items.get(id, id)

    def combine(self, items: Union[Aliases, Dict[str, str]]) -> None:
        if isinstance(items, Aliases):
            self.items = self.items | items.items
        else:
            self.items = self.items | items


@dataclass
class ImportCandidates:
    items: Dict[str, ModulePath]

    def get(self, id: str) -> Optional[ModulePath]:
        return self.items.get(id, None)


@dataclass
class PackageImportBlock:
    name: str
    alias: str
    package: str

    def to_path(self, alias: bool = False) -> ModulePath:
        return find_resource_path(
            package=self.package, alias=self.alias if alias else None, modules=[]
        )

    def __hash__(self) -> int:
        return hash(tuple([self.name, self.alias, self.package]))


@dataclass
class ModuleImportBlock(PackageImportBlock):
    module: List[str]

    def to_path(self, alias: bool = False) -> Union[ModulePath, ItemPath]:
        return find_resource_path(
            package=self.package,
            alias=self.alias if alias else None,
            modules=self.module,
        )

    def __hash__(self) -> int:
        return hash(tuple([self.name, self.alias, self.package] + self.module))


def _split_module(term: str) -> Tuple[str, Optional[List[str]]]:
    terms = term.split(".")
    if len(terms) == 1:
        return terms[0], None
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
                            module=module if isinstance(module, List) else [module],
                            alias=alias.asname
                            if alias.asname is not None
                            else alias.name,
                            name=alias.name,
                        )
                    )
                else:
                    res.append(
                        PackageImportBlock(
                            package=package,
                            alias=alias.asname
                            if alias.asname is not None
                            else alias.name,
                            name=alias.name,
                        )
                    )
            return res

        case ImportFrom(_):
            if item.module is None:
                package = current_package
                module = current_module
            else:
                package, module = _split_module(item.module)
            if module is None:
                module = []
            elif not isinstance(module, List):
                module = [module]
            return [
                ModuleImportBlock(
                    alias=alias.asname if alias.asname is not None else alias.name,
                    package=package,
                    module=[] if module is None else module,
                    name=alias.name,
                )
                for alias in item.names
            ]
