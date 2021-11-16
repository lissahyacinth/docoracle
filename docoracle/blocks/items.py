__all__ = ["ClassBlock", "FunctionBlock"]

from dataclasses import dataclass
from typing import List, Tuple, Optional
from docoracle.blocks.parameters import Parameter, Signature


@dataclass
class FunctionBlock:
    name: str
    lines: Tuple[int, int]
    signature: Signature
    comment_block: Optional[str]


@dataclass
class ClassBlock:
    name: str
    comment_block: str
    lines: Tuple[int, int]
    fields: List[Parameter]
    methods: List[FunctionBlock]
