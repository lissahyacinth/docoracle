from __future__ import annotations

import sys
import pathlib
import logging
from importlib.resources import files

from dataclasses import dataclass, field
from docoracle.discovery import get_local_packages
from typing import List, Optional, Union

LOGGER = logging.getLogger(__name__)

@dataclass
class ModulePath:
    package: str
    module: List[str]
    alias: Optional[str]
    rel_path: pathlib.Path

    def is_package(self) -> bool:
        return len(self.module) == 0

    def __hash__(self) -> int:
        return hash(tuple([self.package, tuple(self.module), self.alias, self.rel_path]))


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


def find_resource_path(
    package: str, 
    modules: List[str],
    alias: Optional[str]
) -> Union[ModulePath, ItemPath]:
    package_block = get_local_packages()[package]
    if package in sys.builtin_module_names:
        builtin_paths = files('docoracle.typeshed_fallback.stdlib')._paths
        base_locations = [next(bp.rglob(f"*{package}*")) for bp in builtin_paths]
    else:
        base_locations = (
            [pathlib.Path(x) for x in package_block.location.submodule_search_locations]
            if package_block.location.submodule_search_locations is not None
            else [pathlib.Path(package_block.location.origin)]
        )
    if len(base_locations) > 1:
        LOGGER.error("More than 1 base loc provided")
        breakpoint()
    else:
        base_location = base_locations[0]
    for module_item in modules:
        next_item = next(base_location.rglob(module_item), None)
        if next_item is not None:
            base_location = base_location / next_item
        else:
            return ItemPath(
                package,
                modules,
                alias,
                base_location,
                module_item
            )
    if base_location.is_dir():
        attempted_location = (base_location / "__init__.py")
        if attempted_location.exists():
            base_location = attempted_location
        else:
            LOGGER.error(f"Could not find module for {base_location}")
    return ModulePath(
        package,
        modules, 
        alias,
        base_location,
    )