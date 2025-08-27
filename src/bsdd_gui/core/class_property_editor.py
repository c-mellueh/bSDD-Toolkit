from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty
from bsdd_gui.module.class_property_editor.constants import (
    SEPERATOR_SECTION,
    SEPERATOR,
    SEPERATOR_STATUS,
)
from bsdd_gui.module.class_property_editor import ui

if TYPE_CHECKING:
    from bsdd_gui import tool


def register_widget(
    widget: ui.ClassPropertyEditor,
    class_editor: Type[tool.ClassPropertyEditor],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    pass


def open_property_info(
    bsdd_class_property: BsddClassProperty,
    class_property_editor: Type[tool.ClassPropertyEditor],
    util: Type[tool.Util],
):
    if window := class_property_editor.get_window(bsdd_class_property):
        if window.isHidden():
            window.close()
            window = class_property_editor.create_window(bsdd_class_property)
    else:
        window = class_property_editor.create_window(bsdd_class_property)
    window.show()
    window.activateWindow()
    window.showNormal()


def splitter_settings_accepted(
    class_property_editor: Type[tool.ClassPropertyEditor], appdata: Type[tool.Appdata]
):
    widget = class_property_editor.get_splitter_settings_widget()
    is_seperator_activated = class_property_editor.get_splitter_settings_checkstate(widget)
    text = class_property_editor.get_splitter_settings_text(widget)
    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")

    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR, text)
    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, is_seperator_activated)
    if not text:
        appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, False)


def connect_signals(
    class_property_editor: Type[tool.ClassPropertyEditor], property_table: Type[tool.PropertyTable]
):
    property_table.signaller.property_info_requested.connect(
        class_property_editor.show_property_info
    )
    class_property_editor.connect_signals()
