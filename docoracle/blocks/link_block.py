from dataclasses import dataclass
from typing import List

from docoracle.discovery.paths import ModulePath


@dataclass
class LinkContext:
    package: str
    module: ModulePath
