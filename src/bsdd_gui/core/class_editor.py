from __future__ import annotations
from PySide6.QtCore import QModelIndex
from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClass
import logging

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_editor import ui


def register_widget(
    widget: ui.ClassEditor, class_editor: Type[tool.ClassEditor], project: Type[tool.Project]
):
    class_editor.register_widget(widget)
    class_editor.register_basic_field(widget, widget.le_name, "Name")
    class_editor.register_basic_field(widget, widget.le_code, "Code")
    class_editor.register_basic_field(widget, widget.te_definition, "Definition")

    widget.le_code.textChanged.connect(
        lambda t, w=widget, d=project.get(): class_editor.validate_code(t, w, d)
    )

    ct_combobox_items = ["Class", "Material", "GroupOfProperties", "AlternativeUse"]
    widget.cb_class_type.addItems(ct_combobox_items)

    # Combo Boxes
    class_editor.register_field_getter(widget, widget.cb_class_type, lambda c: c.ClassType)
    class_editor.register_field_setter(
        widget.cb_class_type,
        lambda v, w=widget: setattr(w.bsdd_class, "ClassType", ct_combobox_items[v]),
    )

    st_combobox_items = ["Preview", "Active", "Inactive"]
    widget.cb_status.addItems(st_combobox_items)

    class_editor.register_field_getter(widget, widget.cb_status, lambda c: c.Status)
    class_editor.register_field_setter(
        widget.cb_status,
        lambda v, w=widget: setattr(w.bsdd_class, "Status", st_combobox_items[v]),
    )

    # Tags
    class_editor.register_field_getter(
        widget, widget.ti_related_ifc_entity, lambda c: c.RelatedIfcEntityNamesList
    )
    class_editor.register_field_setter(
        widget.ti_related_ifc_entity,
        lambda v, w=widget: setattr(w.bsdd_class, "RelatedIfcEntityNamesList", v),
    )


def connect_signals(class_editor: Type[tool.ClassEditor]):
    class_editor.connect_signaller()


def connect_to_main_window(
    class_editor: Type[tool.ClassEditor], main_window: Type[tool.MainWindow]
):
    def emit_class_info_requested(index: QModelIndex):
        index = view.model().mapToSource(index)
        bsdd_class = index.internalPointer()
        if not bsdd_class:
            return
        class_editor.signaller.class_info_requested.emit(bsdd_class)

    view = main_window.get_class_view()
    view.doubleClicked.connect(emit_class_info_requested)


def open_class_editor(bsdd_class: BsddClass, class_editor: Type[tool.ClassEditor]):
    logging.info(f"Open Class Editor for {bsdd_class.Code}")
    widget = class_editor.create_widget(bsdd_class)
    class_editor.sync_from_model(widget)
    widget.show()
