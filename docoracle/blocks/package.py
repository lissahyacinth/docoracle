from __future__ import annotations

__all__ = ["PackageBlock"]

import logging
from typing import Dict, List, Optional, Tuple, Union, Set
from importlib.metadata import version
from docoracle.discovery.paths import ModulePath
from docoracle.blocks.module import (
    ModuleBlock,
    parse_module,
    ReferencedModules,
    ReferenceTable,
)


LOGGER = logging.getLogger(__name__)


class PackageBlock:
    def __init__(
        self,
        name: str,
        version: version,
        modules: Dict[List[str], ModuleBlock],
    ) -> None:
        self.name = name
        self.version = version
        self.modules = modules


def create_reference_table(
    modules: List[ModulePath],
    reference_table: Optional[ReferenceTable] = None,
    linked_modules: Optional[ReferencedModules] = None,
) -> Tuple[ReferenceTable, ReferencedModules]:
    if reference_table is None:
        reference_table = {}
    if linked_modules is None:
        linked_modules = {}
    for module in modules:
        if module not in linked_modules:
            linked_modules[module] = parse_module(module)
        unlinked_modules: Set[ModulePath] = set([])
        for (aliased_module_path, module_path) in linked_modules[
            module
        ].aliases.items():
            if (
                aliased_module_path not in reference_table
                and aliased_module_path.alias != module_path.alias
            ):
                reference_table[aliased_module_path] = module_path
            if module_path not in linked_modules:
                unlinked_modules = unlinked_modules | set([module_path])
        reference_table, linked_modules = create_reference_table(
            list(set(unlinked_modules)), reference_table, linked_modules
        )
    return (reference_table, linked_modules)
