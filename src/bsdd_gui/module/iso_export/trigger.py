from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import iso_export as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.IsoExport,tool.MainWindowWidget,tool.Project)
    core.connect_signals(tool.IsoExport)

def retranslate_ui():
    core.retranslate_ui(tool.IsoExport,tool.MainWindowWidget)

def on_new_project():
    pass

def create_widget(data: object, parent: ui.Widget):
    core.create_widget(data, parent, tool.IsoExport)



def widget_created(widget: ui.Widget):
    core.register_widget(widget, tool.IsoExport)
    core.register_fields(widget, tool.IsoExport)
    core.register_validators(widget, tool.IsoExport, tool.Util)
    core.connect_widget(widget, tool.IsoExport)


def import_settings(widget: ui.Widget):
    core.import_settings(
        widget, tool.IsoExport, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def export_settings(widget: ui.Widget):
    core.export_settings(
        widget, tool.IsoExport, tool.PPClassView, tool.PPPropertyView, tool.Appdata, tool.Popups
    )


def export(widget: ui.Widget):
    core.export(
        widget,
        tool.IsoExport,
        tool.PPClassView,
        tool.PPPropertyView,
        tool.Appdata,
        tool.Popups,
        tool.Util,
        tool.Project
    )
