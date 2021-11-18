from docoracle.blocks import Parameter, Signature, TypeBlock
from docoracle.parse.parse_module import parse_file


def test_parse_module(simple_module):
    mod_ast = parse_file(simple_module)
    assert mod_ast.name == "simple_module"
    assert next(mod_ast.classes()).name == "SimpleClass"
    assert next(mod_ast.classes()).comment_block == "This is my simple class!"
    init_fn = next(mod_ast.classes()).methods[0]
    assert init_fn.signature == Signature(
        parameters=[
            Parameter(name="self", type=TypeBlock(type=None), comment=None),
            Parameter(name="A", type=TypeBlock(type=int), comment=None),
            Parameter(name="B", type=TypeBlock(type=float), comment=None),
        ],
        result=TypeBlock(type=None),
    )
    method_1 = next(mod_ast.classes()).methods[1]
    assert method_1.signature == Signature(
        [Parameter("self", TypeBlock(None), None)], TypeBlock(float)
    )
    assert method_1.comment_block == "Multiply internal numbers together"
