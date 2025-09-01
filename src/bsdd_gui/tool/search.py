from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.search.prop import SearchProperties


class Search:
    @classmethod
    def get_properties(cls) -> SearchProperties:
        return bsdd_gui.SearchProperties
