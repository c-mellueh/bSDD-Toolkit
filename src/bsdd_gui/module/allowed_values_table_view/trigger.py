from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import allowed_values_table_view as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.AllowedValuesTableView, tool.ClassPropertyEditorWidget)


def retranslate_ui():
    pass


def on_new_project():
    pass


def context_menu_requested(view, pos):
    core.create_context_menu(view, pos, tool.AllowedValuesTableView)


def view_created(view: ui.AllowedValuesTable):
    core.register_view(view, tool.AllowedValuesTableView)
    core.add_columns_to_view(view, tool.AllowedValuesTableView)
    core.add_context_menu_to_view(view, tool.AllowedValuesTableView)
    core.connect_view(view, tool.AllowedValuesTableView,tool.Util)

def items_pasted(view:ui.AllowedValuesTable):
    core.item_paste_event(view,tool.AllowedValuesTableView,tool.Util)