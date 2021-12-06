from docoracle.blocks.type_block import TypeBlock
from docoracle.blocks.module import parse_file
from docoracle.blocks.parameters import Parameter, Signature


def test_parse_module(simple_module):
    mod_ast = parse_file(simple_module, package="None")
    assert mod_ast.name == "simple_module"
    assert next(mod_ast.classes()).name == "SimpleClass"
    assert next(mod_ast.classes()).comment_block == "This is my simple class!"
    init_fn = next(mod_ast.classes()).methods[0]
    assert init_fn.signature == Signature(
        parameters=[
            Parameter(name="self", type=None, comment=None),
            Parameter(name="A", string_type="int", type=None, comment=None),
            Parameter(name="B", string_type="float", type=None, comment=None),
        ],
        result=TypeBlock(type=None),
    )
    method_1 = next(mod_ast.classes()).methods[1]
    assert method_1.signature == Signature([Parameter("self", None, None)], "float")
    assert method_1.comment_block == "Multiply internal numbers together"
