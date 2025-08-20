from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict
if TYPE_CHECKING:
    from . import ui

class ClassTreeProperties:
    views: set[ui.ClassView] = set()
