import logging

from typing import Optional, List, Union, Tuple, Dict
from ast import Expr, Constant, FunctionDef


from docoracle.blocks.items import FunctionBlock
from docoracle.blocks.parameters import Parameter, Signature
from docoracle.blocks.type_block import TypeBlock
from docoracle.parse.error import ParseError
from ast import arguments as ast_arguments, Name as ast_Name

from docoracle.parse.parse_parameter import split_parameter_comments


LOGGER = logging.getLogger(__name__)


def _function_comment(f: FunctionDef) -> Optional[Tuple[str, Dict[str, Parameter]]]:
    try:
        function_constant = f.body[0]
        if isinstance(function_constant, Expr):
            function_val = function_constant.value
            if isinstance(function_val, Constant):
                return split_parameter_comments(function_val.value.strip().split("\n"))
    except IndexError:
        return None
    return None


def _method_arguments(
    parameters: Dict[str, Parameter],
    arguments: Union[ast_arguments, List[ast_arguments]],
):
    if not isinstance(arguments, list):
        arguments = [arguments]
    return [
        parameters.get(
            arg.arg,
            Parameter(
                name=arg.arg,
                type=TypeBlock.from_string(arg.annotation.id)
                if isinstance(arg.annotation, ast_Name)
                else TypeBlock(None),  # TODO: Type Inference
                comment="",  # _find_comment
            ),
        )
        for arg in arguments
    ]


def parse_function(item: FunctionDef) -> FunctionBlock:
    function_block_comment = _function_comment(item)
    if function_block_comment is not None:
        block_comment, function_arguments = function_block_comment
    else:
        block_comment, function_arguments = None, {}
    return FunctionBlock(
        item.name,
        (item.lineno, item.end_lineno),
        Signature(
            _method_arguments(function_arguments, item.args.args),
            TypeBlock.from_string(item.returns.id)
            if isinstance(item.returns, ast_Name)
            else TypeBlock(None),  # TODO: Type Inference
        ),
        block_comment,
    )
