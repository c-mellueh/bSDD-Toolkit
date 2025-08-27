from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty
from bsdd_gui.module.class_property_editor.constants import (
    SEPERATOR_SECTION,
    SEPERATOR,
    SEPERATOR_STATUS,
)
from PySide6.QtCore import QCoreApplication
from bsdd_gui.module.class_property_editor import ui
from bsdd_parser.utils import bsdd_class_property as cp_utils

if TYPE_CHECKING:
    from bsdd_gui import tool


def register_widget(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditor],
    property_table: Type[tool.PropertyTable],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    class_property_editor.register_widget(widget)
    class_property_editor.register_basic_field(widget, widget.le_code, "Code")
    class_property_editor.register_basic_field(widget, widget.te_description, "Description")

    # Property Reference Field

    widget.le_property_reference.set_button_text(
        QCoreApplication.translate("ClassPropertyEditor", "Create New")
    )
    class_property_editor.register_field_getter(
        widget, widget.le_property_reference, class_property_editor.get_property_reference
    )
    class_property_editor.register_field_setter(
        widget,
        widget.le_property_reference,
        lambda e, v, p=project: class_property_editor.set_property_reference(e, v, p.get()),
    )
    class_property_editor.register_field_listener(widget, widget.le_property_reference)

    class_property_editor.add_validator(
        widget,
        widget.le_property_reference,
        lambda v, w, p=project: class_property_editor.is_property_reference_valid(
            v, w.bsdd_class_property, p.get()
        ),
        lambda w, v: util.set_invalid(w, not v),
    )

    class_property_editor.add_validator(
        widget,
        widget.le_property_reference,
        lambda v, w, p=project: class_property_editor.is_property_reference_valid(
            v, w.bsdd_class_property, p.get()
        ),
        lambda f, v, w=widget: class_property_editor.handle_property_reference_button(w, f, v),
    )

    # Autoupdate
    class_property_editor.signaller.field_changed.connect(
        lambda w, f: class_property_editor.sync_to_model(w, w.bsdd_class_property, f)
    )

    update_property_specific_fields(widget, class_property_editor)


def update_property_specific_fields(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditor],
):
    if not widget:
        return
    bsdd_class_property = widget.bsdd_class_property

    class_property_editor.update_description_placeholder(widget)


def open_property_info(
    bsdd_class_property: BsddClassProperty,
    class_property_editor: Type[tool.ClassPropertyEditor],
    main_window: Type[tool.MainWindow],
):
    if window := class_property_editor.get_window(bsdd_class_property):
        if window.isHidden():
            window.close()
            window = class_property_editor.create_window(bsdd_class_property, main_window.get())
    else:
        window = class_property_editor.create_window(bsdd_class_property, main_window.get())
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
