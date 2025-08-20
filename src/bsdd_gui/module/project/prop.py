from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bsdd_parser.models import BsddDictionary

class ProjectProperties:
    project_dictionary:BsddDictionary = None
