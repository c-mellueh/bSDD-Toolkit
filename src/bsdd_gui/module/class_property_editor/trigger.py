from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_property_editor as core
from typing import TYPE_CHECKING
from bsdd_parser import BsddClassProperty
from PySide6.QtGui import QKeySequence
from .constants import SEPERATOR_SECTION, SEPERATOR_STATUS
from . import ui, views


def connect():
    tool.Settings.add_page_to_toolbox(
        views.SplitterSettings,
        "pageSplitter",
        lambda: core.splitter_settings_accepted(tool.ClassPropertyEditor, tool.Appdata),
    )
    core.connect_signals(tool.ClassPropertyEditor, tool.PropertyTable)
    # core.create_context_menu_builders(tool.PropertyWidget)


def update_property_specific_fields(window: ui.ClassPropertyEditor):
    core.update_property_specific_fields(window, tool.ClassPropertyEditor)


def retranslate_ui():
    return  # TODO
    core.retranslate_ui(tool.ClassPropertyEditor)


def on_new_project():
    pass


def property_info_requested(som_property: BsddClassProperty):
    core.open_property_info(som_property, tool.ClassPropertyEditor, tool.MainWindow)


def window_created(window: ui.ClassPropertyEditor):
    core.register_widget(
        window, tool.ClassPropertyEditor, tool.PropertyTable, tool.Project, tool.Util
    )


def window_closed(window: ui.ClassPropertyEditor):
    core.unregister_widget(
        window,
        tool.ClassPropertyEditor,
    )


def update_window(window: ui.ClassPropertyEditor):
    return  # TODO

    core.update_window(window, tool.ClassPropertyEditor, tool.Util, tool.Units)


def value_context_menu_request(pos, table_view: ui.ValueView):
    return  # TODO

    core.value_context_menu_request(pos, table_view, tool.ClassPropertyEditor, tool.Util)


def paste_clipboard(table_view: ui.ValueView):
    return  # TODO

    core.handle_paste_event(table_view, tool.ClassPropertyEditor, tool.Appdata)


def copy_table_content(table_view: ui.ValueView):
    return  # TODO

    core.handle_copy_event(table_view, tool.ClassPropertyEditor, tool.Appdata)


# Settings Window


def splitter_settings_created(widget: ui.SplitterSettings):
    return  # TODO

    core.fill_splitter_settings(widget, tool.ClassPropertyEditor, tool.Appdata)


def splitter_checkstate_changed(widget: ui.SplitterSettings):
    return  # TODO

    core.update_splitter_enabled_state(widget, tool.ClassPropertyEditor)
