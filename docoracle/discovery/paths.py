from __future__ import annotations

import sys
import pathlib
import logging
from importlib.resources import files, path

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
        return hash(tuple([self.package, tuple(self.module), self.rel_path]))


@dataclass
class ItemPath(ModulePath):
    item: str

    @staticmethod
    def from_module(module: ModulePath, item: str) -> ItemPath:
        return ItemPath(
            package=module.package,
            module=module.module,
            alias=module.alias,
            rel_path=module.rel_path,
            item=item,
        )

    def to_module(self) -> ModulePath:
        return ModulePath(
            package=self.package,
            module=self.module,
            rel_path=self.rel_path,
            alias=self.alias,
        )

    def __hash__(self) -> int:
        return hash(tuple([self.package] + (self.module) + [self.item]))


def _resolve_init(base_location: pathlib.Path) -> pathlib.Path:
    if base_location.is_dir():
        attempted_location = base_location / "__init__.py"
        if attempted_location.exists():
            base_location = attempted_location
        elif (attempted_location := (base_location / "__init__.pyi")).exists():
            base_location = attempted_location
        else:
            LOGGER.error(f"Could not find module for {base_location}")
    return base_location


def find_resource_path(
    package: str, modules: List[str], alias: Optional[str]
) -> Union[ModulePath, ItemPath]:
    if package in (list(sys.stdlib_module_names) + ["typing_extensions", "_typeshed"]):
        stdlib_path = files("docoracle.typeshed_fallback.stdlib")._paths
        base_location = next(
            filter(
                lambda x: x is not None,
                (
                    [next(bp.rglob(f"{package}.pyi"), None) for bp in stdlib_path]
                    + [next(bp.rglob(f"{package}/"), None) for bp in stdlib_path]
                ),
            )
        )
    elif package in sys.builtin_module_names:
        builtin_paths = files("docoracle.typeshed_fallback")._paths
        base_location = next(
            filter(
                lambda x: x is not None,
                (
                    [next(bp.rglob(f"{package}.pyi"), None) for bp in builtin_paths]
                    + [next(bp.rglob(f"{package}/"), None) for bp in builtin_paths]
                ),
            )
        )
    else:
        try:
            package_block = get_local_packages()[package]
        except KeyError:
            breakpoint()
        base_location = next(
            iter([pathlib.Path(x) for x in package_block.location.submodule_search_locations])
            if package_block.location.submodule_search_locations is not None
            else iter([pathlib.Path(package_block.location.origin)])
        )
    for module_item in modules:
        next_item = next(filter(lambda x: x is not None, iter(
            [
                next(base_location.rglob(f"{module_item}.py"), None),
                next(base_location.rglob(f"{module_item}"), None),
            ])), None)
        if next_item is not None:
            base_location = base_location / next_item
        else:
            return ItemPath(
                package, modules, alias, _resolve_init(base_location), module_item
            )
    return ModulePath(
        package,
        modules,
        alias,
        _resolve_init(base_location),
    )
