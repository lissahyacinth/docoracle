__all__ = ["PackageBlock"]

from dataclasses import dataclass
from typing import Dict, List
from docoracle.blocks.module import ModuleBlock


@dataclass
class PackageBlock:
    name: str
    # Link Item Name to Module Name Candidates, as a name
    # can exist in multiple modules without conflict.
    items: Dict[str, List[str]]
    modules: Dict[List[str], ModuleBlock]
