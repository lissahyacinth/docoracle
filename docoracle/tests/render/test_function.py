from docoracle.parse.parse_function import parse_function
from docoracle.parse.parse_module import _retrieve_file_ast_parse
from docoracle.render import _render_function


def test_function_render(simple_function):
    function_ast = _retrieve_file_ast_parse(simple_function).body[0]
    function_block = parse_function(function_ast)
    print(_render_function(function_block))
    exit(0)


def test_class_render():
    pass


def test_module_render():
    pass
