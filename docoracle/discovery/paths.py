from __future__ import annotations

import pathlib
from dataclasses import dataclass
from docoracle.discovery import get_local_packages
from typing import List


@dataclass
class ModulePath:
    package: str
    module: List[str]

    def rel_path(self) -> pathlib.Path:
        package_block = get_local_packages()[self.package]
        path = package_block.location
        for module in self.module:
            path = path / module
        return path


@dataclass
class ItemPath(ModulePath):
    item: str

    @staticmethod
    def from_module(module: ModulePath, item: str) -> ItemPath:
        return ItemPath(package=module.package, module=module.module, item=item)

    def to_module(self) -> ModulePath:
        return ModulePath(package=self.package, module=self.module)

    def __hash__(self) -> int:
        return hash(self.package + "".join(self.module) + self.item)
