from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import excel as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.Excel, tool.MainWindowWidget, tool.Project)
    core.connect_signals(tool.Excel)


def retranslate_ui():
    core.retranslate_ui(tool.Excel, tool.MainWindowWidget)


def on_new_project():
    pass


def create_widget(data: object, parent: ui.Widget):
    core.create_widget(data, parent, tool.Excel)


# def create_dialog(data: object, parent: ui.Widget):
#    core.create_dialog(data, parent, tool.Excel)


def widget_created(widget: ui.Widget):
    core.register_widget(widget, tool.Excel)
    core.register_fields(widget, tool.Excel)
    core.register_validators(widget, tool.Excel, tool.Util)
    core.connect_widget(widget, tool.Excel)


def import_settings(widget: ui.Widget):
    core.import_settings(
        widget, tool.Excel, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def export_settings(widget: ui.Widget):
    core.export_settings(
        widget, tool.Excel, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def export(widget: ui.Widget):
    core.export(
        widget,
        tool.Excel,
        tool.Appdata,
        tool.Popups,
        tool.Util,
        tool.Project,
        tool.PropertyPicker
    )
