import pathlib

from typing import Dict, Generator, Iterator, Set
from docoracle.blocks.module import ModuleBlock
from docoracle.blocks.package import PackageBlock, UninitializedPackageBlock
from docoracle.parse.parse_module import parse_file
from functools import reduce

from docoracle.utils import _relative_module_path


def submodule_dirs(base_directory: pathlib.Path) -> Set[pathlib.Path]:
    return set(map(lambda x: x.parent, base_directory.rglob("**/__init__.py")))


def ignore_defaults(
    files: Generator[pathlib.Path, None, None]
) -> Iterator[pathlib.Path]:
    return filter(lambda x: x not in ["setup.py"], files)


def parse_package(base_directory: pathlib.Path) -> Dict[str, ModuleBlock]:
    return reduce(
        lambda x, y: x | y,
        [
            {
                _relative_module_path(py_file, base_directory): parse_file(py_file)
                for py_file in ignore_defaults(directory.rglob("*.py"))
            }
            for directory in submodule_dirs(base_directory)
        ],
    )


def initialize_package(package: UninitializedPackageBlock) -> PackageBlock:
    if package.location is None:
        raise RuntimeError("Cannot parse Module without location")
    modules = parse_package(package.location)
    return PackageBlock(name=package.name, version=package.version, modules=modules)
