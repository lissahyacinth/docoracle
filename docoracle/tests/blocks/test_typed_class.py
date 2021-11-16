from docoracle.blocks.parameters import Parameter, Signature
from docoracle.blocks.type_block import TypeBlock
from docoracle.parse.parse_class import parse_class
from ast import ClassDef

from docoracle.parse.parse_module import _retrieve_file_ast_parse


def test_parse_typed_class(typed_class):
    mod_ast = _retrieve_file_ast_parse(typed_class)
    parsed_class = parse_class(next(x for x in mod_ast.body if isinstance(x, ClassDef)))
    assert parsed_class.name == "TypedClass"
    assert parsed_class.comment_block == "This is my typed class!"
    init_fn = parsed_class.methods[0]
    assert init_fn.signature == Signature(
        parameters=[
            Parameter(name="self", type=TypeBlock(type=None), comment=""),
            Parameter(name="A", type=TypeBlock(type=int), comment=""),
            Parameter(name="B", type=TypeBlock(type=float), comment=""),
        ],
        result=TypeBlock(type=None),
    )
