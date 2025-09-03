from __future__ import annotations
from PySide6.QtCore import QModelIndex, QCoreApplication
from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClass
import logging
from bsdd_parser.utils import bsdd_class as class_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_editor_widget import ui


def register_widget(
    widget: ui.ClassEditor,
    class_editor: Type[tool.ClassEditor],
    project: Type[tool.Project],
    util: Type[tool.Util],
    relationship_editor: Type[tool.RelationshipEditor],
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
        lambda e, v: e.set_code(v),
    )

    ct_combobox_items = ["Class", "Material", "GroupOfProperties", "AlternativeUse"]
    widget.cb_class_type.addItems(ct_combobox_items)

    # Combo Boxes
    class_editor.register_field_getter(widget, widget.cb_class_type, lambda c: c.ClassType)
    class_editor.register_field_setter(
        widget,
        widget.cb_class_type,
        lambda e, v: setattr(e, "ClassType", v),
    )

    st_combobox_items = ["Preview", "Active", "Inactive"]
    widget.cb_status.addItems(st_combobox_items)

    class_editor.register_field_getter(widget, widget.cb_status, lambda c: c.Status)
    class_editor.register_field_setter(
        widget,
        widget.cb_status,
        lambda e, v: setattr(e, "Status", v),
    )

    # Tags
    class_editor.register_field_getter(
        widget, widget.ti_related_ifc_entity, lambda c: c.RelatedIfcEntityNamesList
    )
    class_editor.register_field_setter(
        widget,
        widget.ti_related_ifc_entity,
        lambda e, v, w=widget: setattr(e, "RelatedIfcEntityNamesList", v),
    )
    relationship_editor.init_widget(widget.relationship_editor, widget.bsdd_data, mode="dialog")


def connect_signals(class_editor: Type[tool.ClassEditor], project: Type[tool.Project]):
    class_editor.connect_signals()
    class_editor.signals.new_class_created.connect(project.signals.class_added.emit)


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
        class_editor.signals.edit_class_requested.emit(bsdd_class)

    view = main_window.get_class_view()
    view.doubleClicked.connect(emit_class_info_requested)

    main_window.signals.new_class_requested.connect(
        lambda: class_editor.request_new_class(
            class_utils.get_parent(main_window.get_active_class())
        )
    )
    main_window.signals.copy_active_class_requested.connect(
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
        class_editor.sync_to_model(widget, new_class)
        class_editor.signals.new_class_created.emit(new_class)
        class_editor.signals.dialog_accepted.emit(widget)
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
        class_editor.sync_to_model(widget, new_class)
        class_editor.signals.new_class_created.emit(new_class)
        class_editor.signals.dialog_accepted.emit(widget)
    class_editor.unregister_widget(widget)


def open_class_editor(
    bsdd_class: BsddClass, class_editor: Type[tool.ClassEditor], main_window: Type[tool.MainWindow]
):
    dialog = class_editor.create_class_editor_dialog(bsdd_class, main_window.get())
    widget = dialog._editor_widget
    text = QCoreApplication.translate("ClassEditor", "Edit Class")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget, bsdd_class)
        class_editor.signals.dialog_accepted.emit(widget)
    class_editor.unregister_widget(widget)


def group_classes(
    bsdd_classes: list[BsddClass],
    class_editor: Type[tool.ClassEditor],
    main_window: Type[tool.MainWindow],
    project: Type[tool.Project],
    class_tree: Type[tool.ClassTree],
):
    new_class = BsddClass(Code="GroupCode", Name="GroupName", ClassType="Class")
    parent = class_utils.shared_parent(bsdd_classes, dictionary=project.get(), mode="lowest")
    parent_code = None if parent is None else parent.Code
    new_class.ParentClassCode = parent_code
    dialog = class_editor.create_class_editor_dialog(new_class, main_window.get())
    widget = dialog._editor_widget
    text = QCoreApplication.translate("ClassEditor", "Group Classes")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget, new_class)
        class_editor.signals.new_class_created.emit(new_class)
        class_editor.signals.dialog_accepted.emit(widget)
        for child_class in bsdd_classes:
            class_tree.move_class(child_class, new_class, tool.Project)
