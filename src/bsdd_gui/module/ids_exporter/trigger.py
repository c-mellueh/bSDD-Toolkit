from __future__ import annotations
from PySide6.QtCore import QPoint
from bsdd_json import BsddDictionary
from bsdd_gui import tool
from bsdd_gui.core import ids_exporter as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ui import IdsWidget
    from . import model_views


def connect():
    core.connect_to_main_window(tool.IdsExporter, tool.MainWindowWidget, tool.Project)
    core.connect_signals(tool.IdsExporter)


def retranslate_ui():
    core.retranslate_ui(tool.IdsExporter, tool.MainWindowWidget)


def on_new_project():
    pass


def create_widget():
    core.create_widget(tool.IdsExporter, tool.MainWindowWidget, tool.Project)


def widget_created(widget: IdsWidget):
    core.register_widget(widget, tool.IdsExporter)
    core.register_fields(widget, tool.IdsExporter)
    core.register_validators(widget, tool.IdsExporter, tool.Util)
    core.connect_widget(widget, tool.IdsExporter, tool.PPClassView, tool.MainWindowWidget)


def import_settings(widget: IdsWidget):
    core.import_settings(
        widget, tool.IdsExporter, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def export_settings(widget: IdsWidget):
    core.export_settings(
        widget, tool.IdsExporter, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def context_menu_requested(view: model_views.ClassView, pos: QPoint):
    pass
    # TODO: add COntext menu handling
    # core.create_context_menu(view, pos, tool.ItemViewTool)


def export_ids(widget: IdsWidget):
    core.export_ids(
        widget, tool.IdsExporter, tool.PPClassView, tool.PPPropertyView, tool.Popups, tool.Util
    )
