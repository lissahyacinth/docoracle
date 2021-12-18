from __future__ import annotations

import pathlib
import logging
import toml
import subprocess
from docoracle.blocks.import_block import (
    ModuleImportBlock,
    PackageImportBlock,
    parse_import,
)

from docoracle.blocks.items import (
    ClassBlock,
    FunctionBlock,
    parse_class,
    parse_function,
)
from docoracle.discovery.paths import ModulePath

from docoracle.parse import ast3_parse

from typing import TYPE_CHECKING, List, Union, Optional
from functools import lru_cache

from ast import ClassDef, Assign, FunctionDef, AST, Import, ImportFrom

if TYPE_CHECKING:
    from docoracle.blocks.parameters import Parameter


LOGGER = logging.getLogger(__name__)


def retrieve_file_ast_parse(filename: pathlib.Path) -> Optional[AST]:
    return ast3_parse(open(filename).read(), str(filename), "exec")


def parse_item(
    item: Union[ClassDef, FunctionDef, Assign, Import, ImportFrom], path: ModulePath
) -> Union[
    ClassBlock,
    FunctionBlock,
    Parameter,
    List[Union[PackageImportBlock, ModuleImportBlock]],
]:
    match item:
        case ClassDef():
            return parse_class(item)
        case FunctionDef():
            return parse_function(item)
        case Import() | ImportFrom():
            return parse_import(item, path.package, path.module)
        case Assign():
            pass


def _is_root_dir(filename: pathlib.Path) -> bool:
    assert filename.is_dir()
    return (
        (filename / "setup.py").exists()
        or (filename / "pyproject.toml").exists()
        or (not (filename / "__init__.py").exists())
    )


def _check_package_name(filename: pathlib.Path) -> str:
    assert filename.is_dir()
    if (filename / "setup.py").exists():
        name = str(
            subprocess.check_output(
                ["python3", f"{(filename / 'setup.py').absolute().resolve()}", "--name"]
            )
        )
        return name
    if (filename / "pyproject.toml").exists():
        project_metadata = toml.load(filename / "pyproject.toml")
        return str(project_metadata["name"])


@lru_cache()
def find_rel_package(
    filename: pathlib.Path, prev_filename: Optional[pathlib.Path] = None
) -> str:
    while not filename.is_dir() and not _is_root_dir(filename):
        return find_rel_package(filename.parent(), filename)
    if prev_filename is not None:
        return prev_filename.stem
    else:
        _check_package_name(filename)
