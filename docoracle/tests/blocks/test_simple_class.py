from docoracle.blocks.type_block import TypeBlock
from docoracle.blocks.parameters import Parameter, Signature
from docoracle.blocks.items import parse_class
from ast import ClassDef

from docoracle.parse.parse_module import retrieve_file_ast_parse


def test_parse_class(simple_class):
    mod_ast = retrieve_file_ast_parse(simple_class)
    parsed_class = parse_class(next(x for x in mod_ast.body if isinstance(x, ClassDef)))
    assert parsed_class.name == "SimpleClass"
    assert parsed_class.comment_block == "This is my simple class!"
    init_fn = parsed_class.methods[0]
    assert init_fn.signature == Signature(
        parameters=[
            Parameter(name="self", string_type=None, comment=None),
            Parameter(name="A", string_type="int", comment=None),
            Parameter(name="B", string_type="float", comment=None),
        ],
        result=TypeBlock(type=None),
    )
