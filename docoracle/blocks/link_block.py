from dataclasses import dataclass
from typing import List


@dataclass
class LinkContext:
    package: str
    module: List[str]
