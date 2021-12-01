__all__ = ["PackageBlock"]


from typing import Dict, List
from importlib.metadata import version
from docoracle.blocks.module import ModuleBlock


class PackageBlock:
    def __init__(
        self,
        name: str,
        version: version,
        items: Dict[str, List[str]],
        modules: Dict[List[str], ModuleBlock],
    ) -> None:
        self.name = name
        self.version = version
        self.items = items
        self.modules = modules
