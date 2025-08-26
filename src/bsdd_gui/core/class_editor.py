from __future__ import annotations
from PySide6.QtCore import QModelIndex, QCoreApplication
from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClass
import logging
from bsdd_parser.utils import bsdd_class as class_util

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_editor import ui


def register_widget(
    widget: ui.ClassEditor,
    class_editor: Type[tool.ClassEditor],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    class_editor.register_widget(widget)
    class_editor.register_basic_field(widget, widget.le_name, "Name")
    class_editor.register_basic_field(widget, widget.te_definition, "Definition")

    class_editor.add_validator(
        widget,
        widget.le_code,
        lambda v, w, p=project: class_editor.is_code_valid(v, w, p.get()),
        lambda w, v: util.set_invalid(w, not v),
    )
    class_editor.add_validator(
        widget,
        widget.le_name,
        lambda v, w, p=project: class_editor.is_name_valid(v, w, p.get()),
        lambda w, v: util.set_invalid(w, not v),
    )

    class_editor.register_field_getter(widget, widget.le_code, lambda c: c.Code)
    class_editor.register_field_setter(
        widget,
        widget.le_code,
        lambda v, w=widget: w.bsdd_class.set_code(v),
    )

    ct_combobox_items = ["Class", "Material", "GroupOfProperties", "AlternativeUse"]
    widget.cb_class_type.addItems(ct_combobox_items)

    # Combo Boxes
    class_editor.register_field_getter(widget, widget.cb_class_type, lambda c: c.ClassType)
    class_editor.register_field_setter(
        widget,
        widget.cb_class_type,
        lambda v, w=widget: setattr(w.bsdd_class, "ClassType", ct_combobox_items[v]),
    )

    st_combobox_items = ["Preview", "Active", "Inactive"]
    widget.cb_status.addItems(st_combobox_items)

    class_editor.register_field_getter(widget, widget.cb_status, lambda c: c.Status)
    class_editor.register_field_setter(
        widget,
        widget.cb_status,
        lambda v, w=widget: setattr(w.bsdd_class, "Status", st_combobox_items[v]),
    )

    # Tags
    class_editor.register_field_getter(
        widget, widget.ti_related_ifc_entity, lambda c: c.RelatedIfcEntityNamesList
    )
    class_editor.register_field_setter(
        widget,
        widget.ti_related_ifc_entity,
        lambda v, w=widget: setattr(w.bsdd_class, "RelatedIfcEntityNamesList", v),
    )


def connect_signals(class_editor: Type[tool.ClassEditor]):
    class_editor.connect_signaller()


def connect_to_main_window(
    class_editor: Type[tool.ClassEditor],
    main_window: Type[tool.MainWindow],
    project: Type[tool.Project],
):
    def emit_class_info_requested(index: QModelIndex):
        index = view.model().mapToSource(index)
        bsdd_class = index.internalPointer()
        if not bsdd_class:
            return
        class_editor.signaller.edit_class_requested.emit(bsdd_class)

    view = main_window.get_class_view()
    view.doubleClicked.connect(emit_class_info_requested)

    main_window.signaller.new_class_requested.connect(
        lambda: class_editor.request_new_class(main_window.get_active_class())
    )
    main_window.signaller.copy_active_class_requested.connect(
        lambda: class_editor.request_class_copy(main_window.get_active_class())
    )


def create_new_class(
    parent: BsddClass | None,
    class_editor: Type[tool.ClassEditor],
    main_window: Type[tool.MainWindow],
):

    new_class = BsddClass(Code="Code", Name="Name", ClassType="Class")
    new_class.ParentClassCode = parent.Code if parent is not None else None
    dialog = class_editor.create_class_editor_dialog(new_class, main_window.get())
    widget = dialog._editor_widget
    text = QCoreApplication.translate("ClassEditor", "Create New Class")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget)
        class_editor.signaller.new_class_created.emit(new_class)
    class_editor.unregister_widget(widget)


def copy_class(
    old_class: BsddClass,
    class_editor: Type[tool.ClassEditor],
    main_window: Type[tool.MainWindow],
):
    if not old_class:
        return
    new_class = class_editor.copy_class(old_class)
    dialog = class_editor.create_class_editor_dialog(new_class, main_window.get())
    widget = dialog._editor_widget
    text = QCoreApplication.translate("ClassEditor", "Copy Class")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget)
        class_editor.signaller.new_class_created.emit(new_class)
    class_editor.unregister_widget(widget)


def open_class_editor(
    bsdd_class: BsddClass, class_editor: Type[tool.ClassEditor], main_window: Type[tool.MainWindow]
):
    dialog = class_editor.create_class_editor_dialog(bsdd_class, main_window.get())
    widget = dialog._editor_widget
    text = QCoreApplication.translate("ClassEditor", "Edit Class")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget)
    class_editor.unregister_widget(widget)
