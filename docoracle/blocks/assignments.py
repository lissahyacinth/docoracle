from __future__ import annotations

from typing import Optional, Union
from dataclasses import dataclass

from docoracle.blocks.type_block import TypeBlock


@dataclass
class AssignmentBlock:
    name: str
    type: Union[Optional[str], TypeBlock]
    comment: Optional[str]
