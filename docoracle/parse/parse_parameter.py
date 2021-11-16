import sys
import re
import logging
from typing import Optional, Final


LOGGER = logging.getLogger(__name__)

PY_MINOR_VERSION: Final = sys.version_info[1]

from typing import Iterator, List, Dict, Tuple
from docoracle.blocks import Parameter


def _write_parameter(
    parameters: Dict[str, Parameter], current_parameter: str, current_comment: List[str]
):
    parameters[current_parameter] = Parameter(
        current_parameter, None, " ".join(current_comment)
    )


def split_parameter_comments(block: Iterator[str]) -> Tuple[str, Dict[str, Parameter]]:
    comment_block: List[str] = []
    current_parameter: Optional[str] = None
    current_comment: List[str] = []
    double_dot_comment: bool = False
    parameters: Dict[str, Parameter] = {}
    for line in block:
        line = line.strip()
        if (
            len(line) == 0 or line.startswith(":param")
        ) and current_parameter is not None:
            _write_parameter(parameters, current_parameter, current_comment)
            current_comment = []
            current_parameter = None
        if line.startswith(":param"):
            double_dot_comment = False
            current_parameter = re.search(
                r":param\s([a-zA-Z0-9\_\-]+)[\s\:]{1,2}", line
            ).group(1)
            split_comment = re.sub(f":?param\\s{current_parameter}:?", "", line)
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
        _write_parameter(parameters, current_parameter, current_comment)
    # TODO: Rewrite with context management
    return "".join(comment_block).strip(), parameters
