from __future__ import annotations

import logging
import ast

__all__ = ["ClassBlock", "FunctionBlock"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Set, Tuple, Optional, Union, Dict, Iterator
from ast import (
    arguments as ast_arguments,
    ClassDef,
    Assign,
    FunctionDef,
    AnnAssign,
    Expr,
    Constant,
    Name as ast_Name
)
from docoracle.blocks.type_block import TypeBlock
from docoracle.utils import coalesce, flatten_list, str_coalesce
from docoracle.parse.parse_parameter import split_parameter_comments
from docoracle.blocks.parameters import (
    Parameter,
    Signature,
)


LOGGER = logging.getLogger(__name__)


def _function_comment(
    f: FunctionDef,
) -> Optional[Tuple[str, Dict[str, Parameter]]]:
    try:
        function_constant = f.body[0]
        if isinstance(function_constant, Expr):
            function_val = function_constant.value
            if isinstance(function_val, Constant):
                if type(function_val.value) is str:
                    return split_parameter_comments(function_val.value.strip().split("\n"))
                else:
                    return None
    except IndexError:
        return None
    return None


def _combine_parameters(
    comment_parameter: Optional[Parameter],
    ast_parameter: Optional[Parameter],
) -> Parameter:
    if comment_parameter is None or ast_parameter is None:
        return coalesce(comment_parameter, ast_parameter)
    if comment_parameter.type == TypeBlock(None) or ast_parameter.type == TypeBlock(
        None
    ):
        parameter_type = str_coalesce(
            comment_parameter.unevaluated_type, ast_parameter.unevaluated_type
        )
    else:
        parameter_type = ast_parameter.unevaluated_type
    parameter_comment = str_coalesce(comment_parameter.comment, ast_parameter.comment)
    return Parameter(
        name=comment_parameter.name,
        unevaluated_type=parameter_type,
        comment=parameter_comment,
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
                unevaluated_type=arg.annotation,
                comment=None,  # _find_comment
            ),
        )
        for arg in arguments
    ]


def parse_function(
    item: FunctionDef,
    known_parameters: Optional[Dict[str, Parameter]] = None,
) -> FunctionBlock:
    """
    Parse Function AST Details into
    """
    if known_parameters is None:
        known_parameters = {}
    function_block_comment = _function_comment(item)
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
            item.returns.id
            if isinstance(item.returns, ast_Name)
            else TypeBlock(None),  # TODO: Type Inference
        ),
        block_comment,
    )


def _is_comment(ast_item: Expr) -> bool:
    return "value" in ast_item._fields and isinstance(ast_item.value, Constant)


def _retrieve_comment(
    element: Expr,
) -> Optional[Tuple[str, Dict[str, Parameter]]]:
    if not _is_comment(element) or element.value.value is None:
        return None
    else:
        return split_parameter_comments(element.value.value.split("\n"))


def _parse_assignments(assignments: Iterator[Assign]) -> List[List[Parameter]]:
    """
    Assignment can be to multiple targets, but will have a single node value.
    Assign(expr* targets, expr value, string? type_comment)

    # TODO: Deal with Tuple case (a, b = b, a) and ensure assignment
        can be tracked if necessary
    """
    import ast
    for a in assignments:
        print(ast.dump(a))
    return flatten_list(
        [
            [
                Parameter(
                    name=a.targets[target_idx].id,
                    unevaluated_type=a.type_comment,
                    comment=None,
                )
                for target_idx in range(len(a.targets))
            ]
            for a in assignments
        ]
    )


def _parse_annotated_assignments(
    assignments: Iterator[AnnAssign],
) -> List[Parameter]:
    """
    AnnAssign(expr target, expr annotation, expr? value, int simple)
    """
    LOGGER.info(f"Evaluating Parameter {assignments=}")
    return [
        Parameter(
            name=a.target.id,
            unevaluated_type=a.annotation,
            comment=None,
        )
        for a in assignments
    ]


@dataclass
class FunctionBlock:
    name: str
    lines: Tuple[int, int]
    signature: Signature
    comment_block: Optional[str]

    def __hash__(self) -> int:
        return hash(
            tuple([self.name, self.signature, self.comment_block] + list(self.lines))
        )


@dataclass
class ClassBlock:
    name: str
    comment_block: str
    lines: Tuple[int, int]
    fields: List[Parameter]
    methods: List[FunctionBlock]
    _decorators: List[str]

    def __hash__(self) -> int:
        return hash(
            tuple(
                [self.name, self.comment_block, self.lines]
                + self.fields
                + self.methods
                + self._decorators
            )
        )

    def __post_init__(self):
        if "dataclass" in self._decorators:
            self._add_dataclass_init()

    def _add_dataclass_init(self):
        self.methods.append(
            FunctionBlock(
                name="__init__",
                lines=self.lines,
                signature=Signature(parameters=self.fields, result="Self"),
                comment_block=None,
            )
        )


def parse_class(item: ClassDef) -> ClassBlock:
    """
    Map ASTClass Item into relevant Class Documentation Info
    ClassDef(identifier name, - raw string
             expr* bases, - Base Classes
             keyword* keywords, - [keyword](https://docs.python.org/3/library/keyword.html#module-keyword) nodes
             stmt* body, Items
             expr* decorator_list - List of node names
            )

    """
    elements = item.body
    if elements is None or len(elements) == 0:
        return ClassBlock(name=item.name, comment_block=None, fields=[], methods=[])
    comment_param_block = _retrieve_comment(elements[0])
    if comment_param_block is not None:
        comment_block, parameter_comments = comment_param_block
    else:
        comment_block, parameter_comments = None, None
    return ClassBlock(
        name=item.name,
        _decorators=[ast_name.id for ast_name in item.decorator_list],
        comment_block=comment_block,
        lines=(item.lineno, item.end_lineno),
        fields=_parse_assignments(
            (field for field in item.body if isinstance(field, Assign))
        )
        + _parse_annotated_assignments(
            (field for field in item.body if isinstance(field, AnnAssign))
        ),
        methods=[
            parse_function(
                field, parameter_comments if field.name == "__init__" else None
            )
            for field in item.body
            if isinstance(field, FunctionDef)
        ],
    )
