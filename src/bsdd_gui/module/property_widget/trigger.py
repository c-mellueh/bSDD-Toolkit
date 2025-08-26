from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_widget as core
from typing import TYPE_CHECKING
from bsdd_parser import BsddClassProperty
from PySide6.QtGui import QKeySequence
from .constants import SEPERATOR_SECTION, SEPERATOR_STATUS
from . import ui, views


def connect():
    tool.Settings.add_page_to_toolbox(
        views.SplitterSettings,
        "pageSplitter",
        lambda: core.splitter_settings_accepted(tool.PropertyWidget, tool.Appdata),
    )
    core.connect_signals(tool.PropertyWidget, tool.PropertyTable)
    # core.create_context_menu_builders(tool.PropertyWidget)


def retranslate_ui():
    return  # TODO
    core.retranslate_ui(tool.PropertyWindow)


def on_new_project():
    pass


def property_info_requested(som_property: BsddClassProperty):
    core.open_property_info(som_property, tool.PropertyWidget, tool.Util)


def window_created(window: ui.PropertyWindow):
    return  # TODO

    core.init_window(window, tool.PropertyWindow, tool.Util)
    core.connect_window(window, tool.PropertyWindow, tool.Util)
    core.update_window(window, tool.PropertyWindow, tool.Util, tool.Units)


def update_window(window: ui.PropertyWindow):
    return  # TODO

    core.update_window(window, tool.PropertyWindow, tool.Util, tool.Units)


def value_context_menu_request(pos, table_view: ui.ValueView):
    return  # TODO

    core.value_context_menu_request(pos, table_view, tool.PropertyWindow, tool.Util)


def paste_clipboard(table_view: ui.ValueView):
    return  # TODO

    core.handle_paste_event(table_view, tool.PropertyWindow, tool.Appdata)


def copy_table_content(table_view: ui.ValueView):
    return  # TODO

    core.handle_copy_event(table_view, tool.PropertyWindow, tool.Appdata)


# Settings Window


def splitter_settings_created(widget: ui.SplitterSettings):
    return  # TODO

    core.fill_splitter_settings(widget, tool.PropertyWindow, tool.Appdata)


def splitter_checkstate_changed(widget: ui.SplitterSettings):
    return  # TODO

    core.update_splitter_enabled_state(widget, tool.PropertyWindow)
