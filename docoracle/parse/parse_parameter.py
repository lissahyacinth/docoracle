__all__ = ["split_parameter_comment"]

import sys
import re
import ast
import logging
from typing import Optional, Final

LOGGER = logging.getLogger(__name__)

PY_MINOR_VERSION: Final = sys.version_info[1]

from typing import Iterator, List, Dict, Tuple
from docoracle.blocks.parameters import Parameter


def _write_parameter(
    parameters: Dict[str, Parameter],
    parameter_type: Optional[str],
    current_parameter: str,
    current_comment: List[str],
):
    parameters[current_parameter] = Parameter(
        name=current_parameter,
        unevaluated_type=ast.parse(f"{current_parameter}: {parameter_type}")
        .body[0]
        .annotation,
        comment=" ".join(current_comment),
    )


def split_parameter_comments(
    block: Iterator[str],
) -> Tuple[str, Dict[str, Parameter]]:
    comment_block: List[str] = []
    current_parameter: Optional[str] = None
    current_parameter_type: Optional[str] = None
    current_comment: List[str] = []
    double_dot_comment: bool = False
    parameters: Dict[str, Parameter] = {}
    for line in block:
        line = line.strip()
        if (
            len(line) == 0 or line.startswith(":param")
        ) and current_parameter is not None:
            _write_parameter(
                parameters=parameters,
                parameter_type=current_parameter_type,
                current_parameter=current_parameter,
                current_comment=current_comment,
            )
            current_comment = []
            current_parameter = None
        if line.startswith(":param"):
            double_dot_comment = False
            parameter_match = re.search(
                r":param\s([a-zA-Z0-9\_\-]+)\s*([\sa-zA-Z0-9]*)[\s]*:(.*)", line
            )
            if parameter_match is None:
                # TODO: Fix This
                pass
            if (
                parameter_match.group(2) is None
                or len(parameter_match.group(2).strip()) == 0
            ):
                current_parameter = parameter_match.group(1)
                current_parameter_type = None
            else:
                current_parameter = parameter_match.group(2)
                current_parameter_type = parameter_match.group(1).strip()
            split_comment = parameter_match.group(3)
            current_comment = [split_comment.strip()]
        elif len(line) == 0:
            double_dot_comment = False
            if len(comment_block) > 0:
                comment_block[-1] = comment_block[-1].rstrip()
            comment_block += ["\n\n"]
        elif current_parameter is not None:
            current_comment += [line]
        elif not line.startswith("..") and not double_dot_comment:
            comment_block += [line, " "]
        elif line.startswith(".."):
            double_dot_comment = True
        else:
            pass
    if current_parameter is not None:
        _write_parameter(
            parameters, current_parameter_type, current_parameter, current_comment
        )
    # TODO: Rewrite with context management
    if len(comment_block) == 0:
        comment_block = None
    else:
        comment_block = "".join(comment_block).strip()
    return comment_block, parameters
