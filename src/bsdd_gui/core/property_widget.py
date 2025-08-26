from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty
from bsdd_gui.module.property_widget.constants import SEPERATOR_SECTION, SEPERATOR, SEPERATOR_STATUS

if TYPE_CHECKING:
    from bsdd_gui import tool


def open_property_info(
    bsdd_class_property: BsddClassProperty,
    property_window: Type[tool.PropertyWidget],
    util: Type[tool.Util],
):
    if window := property_window.get_window(bsdd_class_property):
        if window.isHidden():
            window.close()
            window = property_window.create_window(bsdd_class_property)
    else:
        window = property_window.create_window(bsdd_class_property)
    window.show()
    window.activateWindow()
    window.showNormal()


def splitter_settings_accepted(
    property_widget: Type[tool.PropertyWidget], appdata: Type[tool.Appdata]
):
    widget = property_widget.get_splitter_settings_widget()
    is_seperator_activated = property_widget.get_splitter_settings_checkstate(widget)
    text = property_widget.get_splitter_settings_text(widget)
    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")

    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR, text)
    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, is_seperator_activated)
    if not text:
        appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, False)


def connect_signals(
    property_widget: Type[tool.PropertyWidget], property_table: Type[tool.PropertyTable]
):
    property_table.signaller.property_info_requested.connect(property_widget.show_property_info)
    property_widget.connect_signals()
