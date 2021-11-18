import logging

from typing import Optional, List, Union, Tuple, Dict
from ast import Expr, Constant, FunctionDef


from docoracle.blocks.items import FunctionBlock
from docoracle.blocks.parameters import Parameter, Signature
from docoracle.blocks.type_block import TypeBlock
from docoracle.parse.error import ParseError
from ast import arguments as ast_arguments, Name as ast_Name

from docoracle.parse.parse_parameter import split_parameter_comments
from docoracle.utils import coalesce, str_coalesce, type_coalesce


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


def _combine_parameters(
    comment_parameter: Optional[Parameter], ast_parameter: Optional[Parameter]
) -> Parameter:
    if comment_parameter is None or ast_parameter is None:
        return coalesce(comment_parameter, ast_parameter)
    if comment_parameter.type == TypeBlock(None) or ast_parameter.type == TypeBlock(
        None
    ):
        parameter_type = type_coalesce(comment_parameter.type, ast_parameter.type)
    else:
        parameter_type = ast_parameter.type
    parameter_comment = str_coalesce(comment_parameter.comment, ast_parameter.comment)
    return Parameter(
        name=comment_parameter.name, type=parameter_type, comment=parameter_comment
    )


def _method_arguments(
    parameters: Dict[str, Parameter],
    arguments: Union[ast_arguments, List[ast_arguments]],
):
    if not isinstance(arguments, list):
        arguments = [arguments]
    return [
        _combine_parameters(
            parameters.get(arg.arg, None),
            Parameter(
                name=arg.arg,
                type=TypeBlock.from_string(arg.annotation.id)
                if isinstance(arg.annotation, ast_Name)
                else TypeBlock(None),
                comment=None,  # _find_comment
            ),
        )
        for arg in arguments
    ]


def parse_function(
    item: FunctionDef, known_parameters: Optional[Dict[str, Parameter]] = None
) -> FunctionBlock:
    """
    Parse Function AST Details into
    """
    if known_parameters is None:
        known_parameters = {}
    function_block_comment = _function_comment(item)
    print(f"{item.name=} {function_block_comment=}")
    if function_block_comment is not None:
        block_comment, function_parameters = function_block_comment
    else:
        block_comment, function_parameters = None, {}
    function_parameters = function_parameters | known_parameters
    return FunctionBlock(
        item.name,
        (item.lineno, item.end_lineno),
        Signature(
            _method_arguments(function_parameters, item.args.args),
            TypeBlock.from_string(item.returns.id)
            if isinstance(item.returns, ast_Name)
            else TypeBlock(None),  # TODO: Type Inference
        ),
        block_comment,
    )
