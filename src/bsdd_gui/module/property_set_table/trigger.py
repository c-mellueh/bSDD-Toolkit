from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_set_list as core
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import ui


def connect():
    pass
def retranslate_ui():
    pass

def on_new_project():
    pass

def table_view_created(view:ui.PsetTableView):
    core.connect_view(view, tool.PropertySetTable, tool.Project, tool.MainWindow)
