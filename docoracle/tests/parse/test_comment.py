from docoracle.blocks.parameters import Parameter
from docoracle.parse.parse_function import split_parameter_comments


def test_split(class_comment):
    block, params = split_parameter_comments(class_comment.split("\n"))
    expected_block = """Represents a blueprint, a collection of routes and other app-related functions that can be registered on a real application later.

A blueprint is an object that allows defining application functions without requiring an application object ahead of time. It uses the same decorators as :class:`~flask.Flask`, but defers the need for an application by recording them for later registration.

Decorating a function with a blueprint creates a deferred function that is called with :class:`~flask.blueprints.BlueprintSetupState` when the blueprint is registered on an application.

See :doc:`/blueprints` for more information."""
    expected_params = {
        "name": Parameter(
            "name",
            None,
            "The name of the blueprint. Will be prepended to each endpoint name.",
        ),
        "import_name": Parameter(
            "import_name",
            None,
            "The name of the blueprint package, usually ``__name__``. This helps locate the ``root_path`` for the blueprint.",
        ),
    }
    assert all(a == b for (a, b) in zip(block.split(" "), expected_block.split(" ")))
    assert (params.items()) == (expected_params.items())
