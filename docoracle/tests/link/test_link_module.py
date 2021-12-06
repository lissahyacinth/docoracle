import pathlib
from docoracle.blocks.module import parse_file


def test_parse_module():
    module_block = parse_file(
        pathlib.Path("/home/eden/GitHub/docoracle/flask/src/flask/app.py"),
        package="flask",
    )
