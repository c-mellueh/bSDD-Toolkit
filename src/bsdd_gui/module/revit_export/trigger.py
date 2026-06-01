from __future__ import annotations
from bsdd_gui import tool
from bsdd_gui.core import revit_export as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.RevitExport, tool.MainWindowWidget, tool.Project)
    core.connect_signals(tool.RevitExport)


def retranslate_ui():
    core.retranslate_ui(tool.RevitExport, tool.MainWindowWidget)


def on_new_project():
    pass


def create_widget(data: object, parent: ui.Widget):
    core.create_widget(data, parent, tool.RevitExport)


# def create_dialog(data: object, parent: ui.Widget):
#    core.create_dialog(data, parent, tool.RevitExport)


def widget_created(widget: ui.Widget):
    core.register_widget(widget, tool.RevitExport)
    core.register_fields(widget, tool.RevitExport)
    core.register_validators(widget, tool.RevitExport, tool.Util)
    core.connect_widget(widget, tool.RevitExport)


def import_settings(widget: ui.Widget):
    core.import_settings(
        widget, tool.RevitExport, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def export_settings(widget: ui.Widget):
    core.export_settings(
        widget, tool.RevitExport, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def export(widget: ui.Widget):
    core.export(widget, tool.RevitExport, tool.Appdata, tool.Popups, tool.Util, tool.Project, tool.Loin)
