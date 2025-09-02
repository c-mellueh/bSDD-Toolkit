# This File can be copied and modified to fit your Module
# It contains the minimum amount of triggers needed to make an ItemView Work

from __future__ import annotations
import bsdd_gui
from typing import TYPE_CHECKING
from bsdd_gui.presets.view_presets import ItemViewType
from PySide6.QtCore import QPoint

from bsdd_gui.presets.core_presets import item_view_preset as core  # <- modify to fit your need
from bsdd_gui.presets import tool_presets as tool  # <- modify to fit your need

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.ItemViewHandler)


def retranslate_ui():
    core.rentranslate_ui(tool.ItemViewHandler)


def on_new_project():
    pass


def context_menu_requested(view: ItemViewType, pos: QPoint):
    core.create_context_menu(view, pos, tool.ItemViewHandler)


def view_created(view: ItemViewType):
    core.register_view(view, tool.ItemViewHandler)
    core.add_columns_to_view(view, tool.ItemViewHandler)
    core.add_context_menu_to_view(view, tool.ItemViewHandler)


def view_closed(view: ItemViewType):
    core.remove_view(view, tool.ItemViewHandler)
