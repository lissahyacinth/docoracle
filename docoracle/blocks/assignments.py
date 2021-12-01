from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING, Dict, Union, Set, List
from dataclasses import dataclass
from docoracle.blocks.link_block import LinkContext

from docoracle.blocks.type_block import TypeBlock
from docoracle.blocks.import_block import ImportBlock, ModuleImportBlock
from docoracle.blocks.items import FunctionBlock, ClassBlock
from docoracle.discovery.paths import ItemPath

if TYPE_CHECKING:
    from docoracle.discovery.paths import ModulePath


@dataclass
class AssignmentBlock:
    name: str
    type: Union[Optional[str], TypeBlock]
    comment: Optional[str]

    def link(
        self,
        item_context: Dict[ItemPath, Union[FunctionBlock, ClassBlock, AssignmentBlock]],
        link_context: LinkContext,
        imports: Dict[str, Union[ImportBlock, ModuleImportBlock]],
    ) -> Set[Union[ItemPath, ModulePath]]:
        """
        Attempt to link all items below the present hierarchy.

        If an item cannot be linked, return the path to the item to be searched.
        If an item cannot be linked, and there's no clues to where it came from,
        return all ModulePaths that are targeted with an import star.
        """
        raise NotImplementedError

    def is_linked(self) -> bool:
        raise NotImplementedError
