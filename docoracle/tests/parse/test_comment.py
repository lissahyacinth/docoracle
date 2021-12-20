from docoracle.blocks.parameters import Parameter
from docoracle.blocks.type_block import NoTypeSpecified, TypeBlock
from docoracle.parse.parse_parameter import split_parameter_comments


def test_split(class_comment):
    block, params = split_parameter_comments(class_comment.split("\n"))
    expected_block = """Represents a blueprint, a collection of routes and other app-related functions that can be registered on a real application later.

A blueprint is an object that allows defining application functions without requiring an application object ahead of time. It uses the same decorators as :class:`~flask.Flask`, but defers the need for an application by recording them for later registration.

Decorating a function with a blueprint creates a deferred function that is called with :class:`~flask.blueprints.BlueprintSetupState` when the blueprint is registered on an application.

See :doc:`/blueprints` for more information."""
    expected_params = {
        "name": Parameter(
            "name",
            TypeBlock(NoTypeSpecified),
            None,
            "The name of the blueprint. Will be prepended to each endpoint name.",
        ),
        "import_name": Parameter(
            "import_name",
            TypeBlock(NoTypeSpecified),
            None,
            "The name of the blueprint package, usually ``__name__``. This helps locate the ``root_path`` for the blueprint.",
        ),
    }
    print(params.items())
    print(expected_params.items())
    for (item, expected_item) in zip(params.items(), expected_params.items()):
        print(f"         {item=}")
        print(f"{expected_item=}")
    assert all(a == b for (a, b) in zip(block.split(" "), expected_block.split(" ")))
    assert (params.items()) == (expected_params.items())
