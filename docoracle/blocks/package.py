__all__ = ["PackageBlock"]

import logging
import sys
from typing import Dict, List, Optional, Tuple, Union
from importlib.metadata import version
from docoracle.blocks.module import ModuleBlock, parse_file
from docoracle.discovery.paths import ItemPath, ModulePath, find_resource_path
from docoracle.discovery import UninitializedPackageBlock, get_local_packages

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


ReferenceTable = Dict[Union[ModulePath, ItemPath], Union[ModulePath, ItemPath]]
ReferencedModules = Dict[ModulePath, ModuleBlock]


def create_reference_table(
    modules: List[ModulePath],
    reference_table: Optional[ReferenceTable] = None,
    linked_modules: Optional[ReferencedModules] = None,
    local_packages: Dict[str, UninitializedPackageBlock] = get_local_packages(),
) -> Tuple[ReferenceTable, ReferencedModules]:
    if reference_table is None:
        reference_table = {}
    if linked_modules is None:
        linked_modules = {}
    for module in [l for l in modules if l not in linked_modules]:
        local_package = local_packages[module.package]
        if local_package.location is None:
            LOGGER.error(f"Cannot find location for {local_package}")
            exit(-1)
        print(local_package)
        print(local_package.location)
        linked_modules[module] = parse_file(module.rel_path, package=module.package)
        unlinked_modules = []
        for (aliased_module_path, module_path) in linked_modules[
            module
        ].aliases.items():
            reference_table[aliased_module_path] = module_path
            unlinked_modules += [module_path]

        create_reference_table(
            list(set(unlinked_modules)), reference_table, linked_modules, local_packages
        )
    return (reference_table, linked_modules)


if __name__ == "__main__":
    
    rt, lm = create_reference_table([find_resource_path("typing", [], None)])
    print(rt)
    print(lm.keys())
