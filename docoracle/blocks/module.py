from __future__ import annotations


__all__ = ["ModuleBlock"]

import pathlib

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Set, Union, Optional
from docoracle.blocks.items import ClassBlock, FunctionBlock
from docoracle.blocks.import_block import ImportBlock
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
from docoracle.utils import relative_module_path

from functools import reduce


def parse_file(
    filename: pathlib.Path,
    package: Optional[str],
    package_modules: Optional[Dict[ModulePath, ModuleBlock]] = None,
) -> ModuleBlock:
    ast_tree = retrieve_file_ast_parse(filename)
    if ast_tree is None:
        raise ParseError
    if package_modules is None:
        package_modules = {}
    return ModuleBlock(
        name=filename.stem if filename.stem != "__init__" else filename.parents[-1],
        package=package if package is not None else find_rel_package(filename),
        relative_name=relative_module_path(filename, filename.parents[0]),
        filepath=filename,
        items={
            item.name: item
            for item in filter(
                lambda x: x is not None, list(map(parse_item, ast_tree.body))
            )
        },
        package_modules=package_modules,
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
    package_modules: Dict[ModulePath, ModuleBlock]
    imports: Dict[str, ImportBlock] = field(default_factory=dict)
    items: Dict[str, Union[ClassBlock, FunctionBlock, AssignmentBlock]] = field(
        default_factory=dict
    )
    context: Dict[ItemPath, Union[FunctionBlock, ClassBlock, AssignmentBlock]] = field(
        default_factory=dict
    )

    def _import_context(
        self,
        marked_items: Set[ItemPath],
        package_modules: Dict[ModulePath, ModuleBlock],
    ) -> Dict[ItemPath, Union[FunctionBlock, ClassBlock, AssignmentBlock]]:
        context: Dict[ItemPath, Union[FunctionBlock, ClassBlock, AssignmentBlock]] = {}
        for item in marked_items:
            block = package_modules.get(item.to_module())
            for (_, item_value) in block.items.items():
                context[item] = item_value
        return context

    def __post_init__(self):
        """
        Perform Import Linking for Classes, Functions, Assignments, etc, within the Module.
        This function mutates self.

        Linking is the process of moving a typed variable from Strings to Context-Rich items.

        Will be left in partial state unless all linked modules are linkable.

        Performs a basic sweep of variables in the immediate module context.
        """
        # Modules to sweep
        link_context = LinkContext(package=self.package, module=self.relative_name)
        marked_items = reduce(lambda x, y: x | y, filter(lambda x: x is not None,(
            [
                value.link(self.context, link_context, self.imports)
                for value in self.items.values()
            ]
        )))
        while len(marked_items) > 0:
            # Parse all modules that are relevant, and not currently parsed.
            for module_path in [
                item.to_module()
                for item in marked_items
                if item.to_module() not in self.package_modules
            ]:
                parsed_module = parse_file(
                    module_path.rel_path(), package_modules=self.package_modules
                )
                self.package_modules[module_path] = parsed_module
            self.context |= self._import_context(marked_items, self.package_modules)
            marked_items = set(
                [
                    value.link(self.context, link_context, self.imports)
                    for value in self.items.values()
                ]
            )

    def __str__(self):
        return (
            f"ModuleBlock (\n"
            f"\t * name={self.name}\n"
            f"\t * classes={self.classes}\n"
            f"\t * items={self.items.items()}\n"
        )

    def named_exports(
        self,
    ) -> Dict[str, Union[ClassBlock, FunctionBlock, AssignmentBlock]]:
        return {x.name: x for x in filter(_is_exported, self.items.values())}

    def classes(self) -> Iterator[ClassBlock]:
        return iter(filter(lambda x: isinstance(x, ClassBlock), self.items.values()))

    def functions(self) -> Iterator[FunctionBlock]:
        return iter(filter(lambda x: isinstance(x, FunctionBlock), self.items.values()))

    def assignments(self) -> Iterator[AssignmentBlock]:
        return iter(
            filter(lambda x: isinstance(x, AssignmentBlock), self.items.values())
        )
