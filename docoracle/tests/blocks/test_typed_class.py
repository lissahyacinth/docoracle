from docoracle.blocks.parameters import Parameter, Signature
from docoracle.blocks.type_block import TypeBlock
from docoracle.blocks.items import parse_class
from docoracle.blocks.module import retrieve_file_ast_parse
from ast import ClassDef


def test_parse_param_typed_class(param_typed_class):
    mod_ast = retrieve_file_ast_parse(param_typed_class)
    parsed_class = parse_class(next(x for x in mod_ast.body if isinstance(x, ClassDef)))
    assert parsed_class.name == "TypedClass"
    assert parsed_class.comment_block == "This is my typed class!"
    init_fn = parsed_class.methods[0]
    assert init_fn.signature == Signature(
        parameters=[
            Parameter(name="self", type=TypeBlock(type=None), comment=None),
            Parameter(name="A", type=TypeBlock(type=int), comment=None),
            Parameter(name="B", type=TypeBlock(type=float), comment=None),
        ],
        result=TypeBlock(type=None),
    )


def test_parse_comment_typed_class(comment_typed_class):
    mod_ast = retrieve_file_ast_parse(comment_typed_class)
    parsed_class = parse_class(next(x for x in mod_ast.body if isinstance(x, ClassDef)))
    assert parsed_class.name == "CommentTypedClass"
    assert parsed_class.comment_block == "This is my comment typed class!"
    init_fn = parsed_class.methods[0]
    print(init_fn.signature)
    assert init_fn.signature == Signature(
        parameters=[
            Parameter(name="self", type=TypeBlock(type=None), comment=None),
            Parameter(name="A", type=TypeBlock(type=int), comment=None),
            Parameter(name="B", type=TypeBlock(type=float), comment=None),
        ],
        result=TypeBlock(type=None),
    )
