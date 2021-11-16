from __future__ import annotations

import pathlib

from typing import Optional

from docoracle.modules import find_modules
from docoracle.parse import PY_MINOR_VERSION, ast3_parse


def main(script_path: Optional[str]):
    if not script_path:
        path = pathlib.Path.cwd()
    else:
        path = pathlib.Path(script_path)
    if not path.exists:
        raise RuntimeError(f"{path} not found")
    init_entrypoint = next(path.rglob("*init__.py"))
    if init_entrypoint is None:
        raise RuntimeError(f"Could not find init file")
    module = find_modules(init_entrypoint)
    for file in module.files:
        ast3_parse(
            open(file).read(), str(file), mode="exec", feature_version=PY_MINOR_VERSION
        )
