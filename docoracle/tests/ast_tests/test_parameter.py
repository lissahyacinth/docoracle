import pytest
import ast
from docoracle.blocks.parameters import UnevaluatedBaseType, UnevaluatedSubscript, retrieve_attribute_type, UnevaluatedList

@pytest.mark.parametrize("test_input,expected", [
    (
        "a: t.typing.Optional[int]", 
        UnevaluatedSubscript(name='t.typing.Optional', inner=UnevaluatedBaseType(name='int'))
    ), 
    (
        "a: Union[t.typing.Optional[int], Optional[bool]]",
        UnevaluatedSubscript(name='Union', inner = UnevaluatedList([
            UnevaluatedSubscript(name='t.typing.Optional', inner=UnevaluatedBaseType(name='int')),
            UnevaluatedSubscript(name='Optional', inner=UnevaluatedBaseType(name='bool'))
        ])) 
    ), 
    (
        "a: int | bool",
        UnevaluatedList(
                inner=[
                UnevaluatedBaseType(name='int'),
                UnevaluatedBaseType(name='bool'),
            ]
        )
    ),
    (
        "a: t.typing.Optional[Union[int, bool]]", 
        UnevaluatedSubscript(
            name='t.typing.Optional', 
            inner=UnevaluatedSubscript(
                name='Union', 
                inner=UnevaluatedList(
                    inner=[
                        UnevaluatedBaseType(name='int'), 
                        UnevaluatedBaseType(name='bool')
                        ]
                )
            )
        )
    )
    ])
def test_parse_parameter_from_ast(test_input, expected):
    assert retrieve_attribute_type(ast.parse(test_input).body[0].annotation) == expected