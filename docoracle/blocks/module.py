from __future__ import annotations
import functools


__all__ = ["ModuleBlock"]

import pathlib

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Set, Union, Optional
from docoracle.blocks.items import ClassBlock, FunctionBlock
from docoracle.blocks.import_block import ModuleImportBlock, PackageImportBlock
from docoracle.blocks.link_block import LinkContext
from docoracle.parse.error import ParseError
from docoracle.parse.parse_module import (
    parse_item,
    find_rel_package,
    retrieve_file_ast_parse,
)
from docoracle.blocks.assignments import AssignmentBlock
from docoracle.discovery.paths import ModulePath, ItemPath
from docoracle.parse.error import ParseError
from docoracle.utils import flatten_list, relative_module_path

from functools import cached_property


def parse_file(
    filename: pathlib.Path,
    package: Optional[str],
) -> ModuleBlock:
    ast_tree = retrieve_file_ast_parse(filename)
    if ast_tree is None:
        raise ParseError
    package_name = package if package is not None else find_rel_package(filename)
    module_name = relative_module_path(filename, filename.parents[0])
    context_parse = functools.partial(
        parse_item, context=LinkContext(package=package_name, module=module_name)
    )
    return ModuleBlock(
        name=filename.stem if filename.stem != "__init__" else filename.parents[-1],
        package=package_name,
        relative_name=module_name if isinstance(module_name, list) else [module_name],
        filepath=filename,
        items={
            item
            for item in flatten_list(
                filter(
                    lambda x: x is not None, list(map(context_parse, ast_tree.body))
                ),
            )
        },
    )



def _is_exported(item: Union[FunctionBlock, AssignmentBlock, ClassBlock]) -> bool:
    match item:
        case FunctionBlock(f_name):
            return not f_name.startswith("_")
        case AssignmentBlock(a_name):
            return not a_name.startswith("_")
        case ClassBlock(c_name):
            return not c_name.startswith("_")
        case _:
            return False


@dataclass
class ModuleBlock:
    name: str
    package: str
    relative_name: List[str]
    filepath: pathlib.Path
    items: Set[Union[ClassBlock, FunctionBlock, AssignmentBlock]] = field(
        default_factory=set
    )

    def __hash__(self) -> int:
        return hash(
            tuple(
                [
                    self.name,
                    self.package,
                    self.filepath,
                ]
                + self.relative_name
                + self.items
            )
        )

    @cached_property
    def named_exports(
        self,
    ) -> Set[str]:
        return set(x.name for x in filter(_is_exported, self.items))

    def classes(self) -> Iterator[ClassBlock]:
        return iter(filter(lambda x: isinstance(x, ClassBlock), self.items))

    def functions(self) -> Iterator[FunctionBlock]:
        return iter(filter(lambda x: isinstance(x, FunctionBlock), self.items))

    def assignments(self) -> Iterator[AssignmentBlock]:
        return iter(filter(lambda x: isinstance(x, AssignmentBlock), self.items))

    @cached_property
    def aliases(self) -> Dict[Union[ItemPath, ModulePath], Union[ItemPath, ModulePath]]:
        """
        TODO: Add in Assignments
        """
        return {
            x.to_path(alias=True): x.to_path(alias=False)
            for x in self.items
            if (isinstance(x, ModuleImportBlock) or isinstance(x, PackageImportBlock))
        }

    @cached_property
    def imports(self) -> Set[ModulePath]:
        return {
            x.to_path()
            for x in self.items.values()
            if (isinstance(x, ModuleImportBlock) or isinstance(x, PackageImportBlock))
        }

    def package_imports(self) -> Set[ModulePath]:
        return {
            x
            for x in filter(
                lambda x: isinstance(x, PackageImportBlock),
                self.items.values(),
            )
        }

    def __str__(self):
        return (
            f"ModuleBlock (\n"
            f"\t * name={self.name}\n"
            f"\t * classes={self.classes}\n"
            f"\t * items={self.items}\n"
        )
