from __future__ import annotations


__all__ = ["ModuleBlock"]


from dataclasses import dataclass, field
from typing import Dict, Iterator, Set, Union, Optional
from docoracle.blocks.items import ClassBlock, FunctionBlock
from docoracle.blocks.import_block import ModuleImportBlock, PackageImportBlock
from docoracle.parse.error import ParseError
from docoracle.parse.parse_module import (
    parse_item,
    retrieve_file_ast_parse,
)
from docoracle.blocks.assignments import AssignmentBlock
from docoracle.discovery.paths import ModulePath, ItemPath
from docoracle.parse.error import ParseError
from docoracle.utils import flatten_list

from functools import cached_property, partial


def parse_module(
    module: ModulePath,
) -> ModuleBlock:
    ast_tree = retrieve_file_ast_parse(module.rel_path)
    if ast_tree is None:
        raise ParseError
    parse = partial(parse_item, path=module)
    return ModuleBlock(
        name=module.module[-1] if len(module.module) > 0 else None,
        path=module,
        items={
            item
            for item in flatten_list(
                filter(lambda x: x is not None, list(map(parse, ast_tree.body))),
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
    name: Optional[str]
    path: ModulePath
    items: Set[Union[ClassBlock, FunctionBlock, AssignmentBlock]] = field(
        default_factory=set
    )

    def __hash__(self) -> int:
        return hash(
            tuple(
                [
                    self.name,
                    self.path,
                ]
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

    def fetch_item(
        self, item: ItemPath
    ) -> Union[None, ClassBlock, FunctionBlock, AssignmentBlock]:
        return next((i for i in self.items if i == item), None)

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

    def link(
        self,
        reference_table: ReferenceTable,
        referenced_modules: ReferencedModules,
    ):
        for item in self.items:
            match item:
                case PackageImportBlock() | ModuleImportBlock():
                    pass
                case _:
                    item.link(
                        module=self.path,
                        reference_table=reference_table,
                        referenced_modules=referenced_modules,
                    )


ReferenceTable = Dict[Union[ModulePath, ItemPath], Union[ModulePath, ItemPath]]
ReferencedModules = Dict[ModulePath, ModuleBlock]
