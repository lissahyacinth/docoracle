import pytest
import pathlib

from importlib.resources import files


@pytest.fixture()
def class_comment() -> str:
    return """Represents a blueprint, a collection of routes and other app-related functions that can be registered on a real application later.

    A blueprint is an object that allows defining application functions without requiring an application object ahead of time. It uses the same decorators as :class:`~flask.Flask`, but defers the need for an application by recording them for later registration.

    Decorating a function with a blueprint creates a deferred function that is called with :class:`~flask.blueprints.BlueprintSetupState` when the blueprint is registered on an application.

    See :doc:`/blueprints` for more information.

    :param name: The name of the blueprint. Will be prepended to each
        endpoint name.
    :param import_name: The name of the blueprint package, usually
        ``__name__``. This helps locate the ``root_path`` for the
        blueprint.

    .. versionchanged:: 1.1.0
        Blueprints have a ``cli`` group to register nested CLI commands.
        The ``cli_group`` parameter controls the name of the group under
        the ``flask`` command.

    .. versionadded:: 0.7
    """


@pytest.fixture()
def simple_class() -> pathlib.PosixPath:
    return files("docoracle.tests.resources").joinpath("simple_class.py")


@pytest.fixture()
def simple_function() -> pathlib.PosixPath:
    return files("docoracle.tests.resources").joinpath("simple_function.py")


@pytest.fixture()
def simple_dataclass() -> pathlib.PosixPath:
    return files("docoracle.tests.resources").joinpath("dataclass.py")


@pytest.fixture()
def dataclass_with_comment() -> pathlib.PosixPath:
    return files("docoracle.tests.resources").joinpath("dataclass_comments.py")


@pytest.fixture()
def param_typed_class() -> pathlib.PosixPath:
    return files("docoracle.tests.resources").joinpath("param_typed_class.py")


@pytest.fixture()
def comment_typed_class() -> pathlib.PosixPath:
    return files("docoracle.tests.resources").joinpath("comment_typed_class.py")


@pytest.fixture()
def simple_module() -> pathlib.PosixPath:
    return files("docoracle.tests.resources").joinpath("simple_module.py")
