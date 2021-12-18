import pytest
import ast
from docoracle.blocks.parameters import (
    BaseType,
    TypeSubScript,
    retrieve_attribute_type,
    TypeList,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            "a: t.typing.Optional[int]",
            TypeSubScript(name="t.typing.Optional", inner=BaseType(name="int")),
        ),
        (
            "a: Union[t.typing.Optional[int], Optional[bool]]",
            TypeSubScript(
                name="Union",
                inner=TypeList(
                    [
                        TypeSubScript(
                            name="t.typing.Optional",
                            inner=BaseType(name="int"),
                        ),
                        TypeSubScript(name="Optional", inner=BaseType(name="bool")),
                    ]
                ),
            ),
        ),
        (
            "a: int | bool",
            TypeList(
                inner=[
                    BaseType(name="int"),
                    BaseType(name="bool"),
                ]
            ),
        ),
        (
            "a: t.typing.Optional[Union[int, bool]]",
            TypeSubScript(
                name="t.typing.Optional",
                inner=TypeSubScript(
                    name="Union",
                    inner=TypeList(
                        inner=[
                            BaseType(name="int"),
                            BaseType(name="bool"),
                        ]
                    ),
                ),
            ),
        ),
    ],
)
def test_parse_parameter_from_ast(test_input, expected):
    assert retrieve_attribute_type(ast.parse(test_input).body[0].annotation) == expected
