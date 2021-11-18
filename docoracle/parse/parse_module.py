import pathlib
import logging
from docoracle.blocks import ClassBlock, FunctionBlock, ModuleBlock, Parameter

from docoracle.parse import ast3_parse
from docoracle.parse.parse_class import parse_class
from typing import Union, Optional

from ast import (
    ClassDef,
    Assign,
    FunctionDef,
    AST
)
from docoracle.parse.error import ParseError

from docoracle.parse.parse_function import parse_function


LOGGER = logging.getLogger(__name__)


def _retrieve_file_ast_parse(filename: pathlib.Path) -> Optional[AST]:
    return ast3_parse(open(filename).read(), str(filename), "exec")

def _parse_item(item: Union[ClassDef, FunctionDef, Assign]) -> Union[ClassBlock, FunctionBlock, Parameter]:
    match item:
        case ClassDef():
            return parse_class(item)
        case FunctionDef():
            return parse_function(item)
        case Assign():
            raise NotImplementedError

def parse_file(filename: pathlib.Path) -> ModuleBlock:
    ast_tree = _retrieve_file_ast_parse(filename)
    if ast_tree is None:
        raise ParseError
    return ModuleBlock(
        filename.stem if filename.stem != '__init__' else filename.parents[-1],
        '', # TODO: Add Relative Name
        filename,
        items=list(map(_parse_item, ast_tree.body)),
    )
                   


