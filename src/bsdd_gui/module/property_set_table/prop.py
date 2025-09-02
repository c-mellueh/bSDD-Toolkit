from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui
from bsdd_parser import BsddClass
from bsdd_gui.presets.prop_presets import ViewProperties


class PropertySetTableProperties(ViewProperties):
    views: set[ui.PsetTableView] = set()
    temporary_pset: dict[BsddClass, list[str]] = dict()
