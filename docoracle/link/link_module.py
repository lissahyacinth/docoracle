"""
A subset of all types in a module must be assessed.

In each module, identify the subset as either a marked subset from
another module, or all items.

In each module
    marked_modules: Dict[str, List[str]] = {}
    Module Name -> Item Names to Check

    module_context: Dict[str, Any] = {}
    for item in module.items():
        # If the item is locally defined, add the type to the module context.
        local_link(item, module_context)
"""

from typing import *
from docoracle.blocks.type_block import TypeBlock

marked_modules = Dict[str, List[str]]
module_context: Dict[str, TypeBlock]


def link_module() -> Tuple[marked_modules, module_context]:
    pass
