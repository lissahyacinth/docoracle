__all__ = ["Parameter", "Signature"]

from dataclasses import dataclass
from typing import List, Optional
from docoracle.blocks.type_block import TypeBlock


@dataclass
class Parameter:
    name: str
    type: TypeBlock
    comment: Optional[str]


@dataclass
class Signature:
    parameters: List[Parameter]
    result: TypeBlock

    def __str__(self) -> str:
        lhs = [f"{param.name} : {param.type}" for param in self.parameters]
        rhs = f"{self.result.type}"
        return f"({', '.join(lhs)}) -> {rhs}"
