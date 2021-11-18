import pathlib
import logging

from typing import Dict, Optional, List, Iterator, Tuple
from ast import ClassDef, Expr, Constant, Assign, FunctionDef

from docoracle.blocks import ClassBlock, FunctionBlock, Parameter, TypeBlock
from docoracle.parse.error import ParseError

from docoracle.parse.parse_function import parse_function
from docoracle.parse.parse_parameter import split_parameter_comments


LOGGER = logging.getLogger(__name__)

def _is_comment(ast_item: Expr) -> bool:
    return "value" in ast_item._fields and isinstance(ast_item.value, Constant)


def _retrieve_comment(element: Expr) -> Optional[Tuple[str, Dict[str, Parameter]]]:
    if not _is_comment(element):
        return None
    else:
        return split_parameter_comments(element.value.value.split('\n'))

def _find_text_comment(file: pathlib.Path, lines: Tuple[int, int]) -> Optional[str]:
    raise NotImplementedError

def _field_to_parameter(
    a: Assign,
    idx: int,
) -> Parameter:
    """
    """
    field_name: str = a.targets[idx].id
    return Parameter(
                        name=field_name,
                        type=(
                            TypeBlock.from_string(a.type_comment) 
                            if a.type_comment is not None 
                            else TypeBlock.infer_type_from_string(a.targets[idx].value)
                        ),
                        comment=None# _get_field_comment()
    )

def _parse_fields(assignments: Iterator[Assign]) -> List[Parameter]:
    """
        Combine Field Information from Comment Block and Assignment

        :param assignments: AST Assignments of fields, i.e. Within the class; 
            class X:
                y : int = 0
            y is captured as an assignment.
    """
    parameters = []
    for a in assignments:
        match len(a.targets):
            case 0:
                LOGGER.warning(f"Assignment has no targets")
            case 1:
                parameters.append(
                    _field_to_parameter(a, 0)
                )
            case _:
                for target_idx in range(len(a.targets)):
                    parameters.append(
                    _field_to_parameter(a, target_idx)
                )
    return parameters


def parse_class(item: ClassDef) -> ClassBlock:
    """
        Map ASTClass Item into relevant Class Documentation Info 
    """
    elements = item.body
    if elements is None or len(elements) == 0:
        return ClassBlock(
            name=item.name, 
            comment_block=None,
            fields=[],
            methods=[]
        )
    comment_param_block = _retrieve_comment(elements[0])
    if comment_param_block is not None:
        comment_block, parameter_comments = comment_param_block
    else:
        comment_block, parameter_comments  = None, None
    return ClassBlock(
        name=item.name,
        comment_block=comment_block,
        lines=(item.lineno, item.end_lineno),
        fields=_parse_fields((field for field in item.body if isinstance(field, Assign))),
        methods=[
            parse_function(field, parameter_comments if field.name == '__init__' else None) for field in item.body if isinstance(field, FunctionDef)
        ],
    )
