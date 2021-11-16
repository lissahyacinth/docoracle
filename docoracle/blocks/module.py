from __future__ import annotations

__all__ = ["ModuleBlock"]

import pathlib

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Iterator, List, Union, Set
from docoracle.blocks.items import ClassBlock, FunctionBlock
from ast import alias as ast_alias, Import as ast_import


class ImportType(Enum):
    module = auto()
    submodule = auto()
    item = auto()

    @staticmethod
    def detect_type(item: ast_import, alias: ast_alias) -> ImportType:
        raise NotImplementedError


@dataclass
class ImportModuleBlock:
    name: str
    aliased_name: str


@dataclass
class ImportItemBlock:
    package: str
    module: List[str]
    name: str
    aliased_name: str
    type: ImportType


def _parse_import(item: ast_import) -> List[Union[ImportItemBlock, ImportModuleBlock]]:
    if hasattr(item, "module"):
        pass
    else:
        pass
    module = item.module if hasattr(item, "module").split(".") else None
    return [
        ImportBlock(
            package=module[0] if module is not None else alias.name,
            module=module,
            name=alias.name,
            aliased_name=alias.asname,
            type=ImportType.detect_type(item, alias),
        )
        for alias in item.names
    ]


@dataclass
class ModuleBlock:
    name: str
    relative_name: List[str]
    filepath: pathlib.Path
    """
        Imports can take multiple forms;
            import package
            import package as package_two
            from package import module
            from package import item
    """
    imports: Set[pathlib.Path] = field(default_factory=set)
    items: Dict[str, Union[ClassBlock, FunctionBlock]] = field(default_factory=dict)

    def __str__(self):
        return (
            f"ModuleBlock (\n"
            f"\t * name={self.name}\n"
            f"\t * classes={self.classes}\n"
            f"\t * items={self.items.items()}\n"
        )

    def classes(self) -> Iterator[ClassBlock]:
        return filter(lambda x: isinstance(x, ClassBlock), self.items)

    def functions(self) -> Iterator[ClassBlock]:
        return filter(lambda x: isinstance(x, FunctionBlock), self.items)
