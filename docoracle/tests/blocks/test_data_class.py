from docoracle.blocks.type_block import TypeBlock
from docoracle.blocks.items import parse_class
from docoracle.blocks.parameters import Parameter, Signature
from docoracle.parse.parse_module import retrieve_file_ast_parse
from ast import ClassDef


def test_parse_simple_dataclass(simple_dataclass):
    mod_ast = retrieve_file_ast_parse(simple_dataclass)
    parsed_class = parse_class(
        next(x for x in mod_ast.body if isinstance(x, ClassDef)),
    )
    assert parsed_class.name == "DataClassNoComments"
    assert parsed_class.comment_block is None
    assert parsed_class.fields == [
        Parameter(name="A", string_type="int", comment=None),
        Parameter(name="B", string_type="float", comment=None),
    ]


def test_parse_comment_dataclass(dataclass_with_comment):
    """
    This test *will* fail until a function is written to identify comments from
    the raw file, instead of working from the AST.
    """
    mod_ast = retrieve_file_ast_parse(dataclass_with_comment)
    parsed_class = parse_class(next(x for x in mod_ast.body if isinstance(x, ClassDef)))
    assert parsed_class.name == "DataClassWithComments"
    assert parsed_class.comment_block is None
    init_fn = parsed_class.methods[1]
    assert init_fn.signature == Signature(
        parameters=[
            Parameter(name="self", string_type=None, type=None, comment=None),
            Parameter(name="A", string_type="int", type=None, comment="LHS Integer"),
            Parameter(name="B", string_type="float", type=None, comment="RHS Float"),
        ],
        result=TypeBlock(type=None),
    )
