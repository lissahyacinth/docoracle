from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union, Tuple
from ast import Import, ImportFrom

from docoracle.discovery.paths import ModulePath


@dataclass
class ModuleImportBlock:
    name: str
    _alias: str
    package: str

    def to_path(self) -> ModulePath:
        return ModulePath(package=self.package, module=[])


@dataclass
class ImportBlock(ModuleImportBlock):
    module: List[str]

    def to_path(self) -> ModulePath:
        return ModulePath(package=self.package, module=self.module)


def _split_module(term: str) -> Tuple[Optional[str], List[str]]:
    terms = term.split(".")
    if len(terms) == 1:
        return None, terms
    return terms.pop(0), terms


def parse_import(
    item: Union[Import, ImportFrom]
) -> List[Union[ModuleImportBlock, ImportBlock]]:
    match item:
        case Import(_):
            return [
                ModuleImportBlock(
                    alias=alias.name, package=None, module=None, item=None
                )
                for alias in item.names
            ]

        case ImportFrom(_):
            package, module = _split_module(item.module)
            return [
                ImportBlock(
                    alias=alias.asname, package=package, module=module, item=alias.name
                )
                for alias in item.names
            ]
