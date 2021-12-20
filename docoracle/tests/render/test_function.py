from docoracle.blocks.items import parse_function
from docoracle.render import _render_function
from docoracle.parse.parse_module import retrieve_file_ast_parse


def test_function_pre_link_render(simple_function):
    expected_render = [
        "# my_function",
        "(a : int) -> float",
        "## Parameters",
        "a : int",
        "\tA number of some kind: or something",
        "## Description",
        "This is my function!",
    ]
    function_ast = retrieve_file_ast_parse(simple_function).body[0]
    function_block = parse_function(function_ast)
    print(function_block)
    for (line, actual_line) in zip(
        _render_function(function_block).split("\n"),
        expected_render,
    ):
        print(f"       {line=}")
        print(f"{actual_line=}\n")
    assert _render_function(function_block) == "\n".join(expected_render)


def test_class_render():
    pass


def test_module_render():
    pass
