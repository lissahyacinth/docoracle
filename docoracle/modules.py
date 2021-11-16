from __future__ import annotations

import pathlib
from sys import path

from typing import Optional, List, Set, Any
from dataclasses import dataclass, field


@dataclass
class ModuleInfo:
    root: pathlib.Path
    files: Set[pathlib.Path]
    submodules: Set[ModuleInfo] = field(default_factory=set)


def find_modules(src: pathlib.Path) -> ModuleInfo:
    parent_dir = src if src.is_dir() else src.parents[0]
    submodules = set()
    files = set()
    root: Optional[pathlib.Path] = None
    for file in parent_dir.glob():
        if file.name == "__init__":
            root = file
        elif file.is_dir():
            submodules = submodules | {find_modules(file)}
        else:
            files = files | {file}
    if root is None:
        raise RuntimeError(f"Could not find __init__.py file in {src}")
    return ModuleInfo(root, files, submodules)
