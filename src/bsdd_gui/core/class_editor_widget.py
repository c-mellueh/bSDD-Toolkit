from __future__ import annotations
from PySide6.QtCore import QModelIndex, QCoreApplication, QTimer
from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClass
import logging
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui.presets.ui_presets.waiting import start_waiting_widget, stop_waiting_widget

import json

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_editor_widget import ui


def connect_signals(class_editor: Type[tool.ClassEditorWidget], project: Type[tool.Project]):
    class_editor.connect_signals()
    class_editor.signals.related_ifc_added.connect(project.signals.ifc_relation_addded.emit)
    class_editor.signals.related_ifc_removed.connect(project.signals.ifc_relation_removed.emit)


def retranslate_ui(class_editor: Type[tool.ClassEditorWidget]):
    pass  # TODO


def create_dialog(
    bsdd_class: BsddClass,
    class_editor: Type[tool.ClassEditorWidget],
    main_window: Type[tool.MainWindowWidget],
):
    dialog = class_editor.create_dialog(bsdd_class, main_window.get())
    text = QCoreApplication.translate("ClassEditor", "Edit Class")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(dialog._widget, bsdd_class)
        class_editor.signals.dialog_accepted.emit(dialog)
    else:
        class_editor.signals.dialog_declined.emit(dialog)


def register_widget(widget: ui.ClassEditor, class_editor: Type[tool.ClassEditorWidget]):
    class_editor.register_widget(widget)

    ct_combobox_items = ["Class", "Material", "GroupOfProperties", "AlternativeUse"]
    widget.cb_class_type.addItems(ct_combobox_items)
    st_combobox_items = ["Active", "Inactive"]
    widget.cb_status.addItems(st_combobox_items)


def register_fields(widget: ui.ClassEditor, class_editor: Type[tool.ClassEditorWidget]):
    class_editor.register_basic_field(widget, widget.le_name, "Name")
    class_editor.register_basic_field(widget, widget.te_definition, "Definition")

    class_editor.register_field_getter(widget, widget.le_code, lambda c: c.Code)
    class_editor.register_field_setter(widget, widget.le_code, lambda e, v: cl_utils.set_code(e, v))

    class_editor.register_field_getter(widget, widget.cb_class_type, lambda c: c.ClassType)
    class_editor.register_field_setter(
        widget, widget.cb_class_type, lambda e, v: setattr(e, "ClassType", v)
    )

    class_editor.register_field_getter(widget, widget.cb_status, lambda c: c.Status)
    class_editor.register_field_setter(
        widget, widget.cb_status, lambda e, v: setattr(e, "Status", v)
    )

    class_editor.register_field_getter(
        widget, widget.ti_related_ifc_entity, lambda c: c.RelatedIfcEntityNamesList
    )
    class_editor.register_field_setter(
        widget,
        widget.ti_related_ifc_entity,
        lambda e, v, w=widget: setattr(e, "RelatedIfcEntityNamesList", v),
    )


def register_validators(
    widget,
    class_editor: Type[tool.ClassEditorWidget],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
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


def connect_widget(
    widget: ui.ClassEditor,
    class_editor: Type[tool.ClassEditorWidget],
    relationship_editor: Type[tool.RelationshipEditorWidget],
):
    class_editor.connect_widget_signals(widget)
    relationship_editor.init_widget(widget.relationship_editor, widget.bsdd_data, mode="dialog")


def connect_to_main_window(
    class_editor: Type[tool.ClassEditorWidget], main_window: Type[tool.MainWindowWidget]
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
        lambda: class_editor.request_new_class(cl_utils.get_parent(main_window.get_active_class()))
    )
    main_window.signals.copy_active_class_requested.connect(
        lambda: class_editor.request_class_copy(main_window.get_active_class())
    )


def create_new_class(
    parent: BsddClass | None,
    class_editor: Type[tool.ClassEditorWidget],
    main_window: Type[tool.MainWindowWidget],
):

    new_class = BsddClass(Code="Code", Name="Name", ClassType="Class")
    new_class.ParentClassCode = parent.Code if parent is not None else None
    dialog = class_editor.create_dialog(new_class, main_window.get())
    widget = dialog._widget
    text = QCoreApplication.translate("ClassEditor", "Create New Class")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget, new_class)
        class_editor.signals.new_class_created.emit(new_class)
        class_editor.signals.dialog_accepted.emit(dialog)
    else:
        class_editor.signals.dialog_declined.emit(dialog)

    class_editor.unregister_widget(widget)


def copy_class(
    old_class: BsddClass,
    class_editor: Type[tool.ClassEditorWidget],
    main_window: Type[tool.MainWindowWidget],
):
    if not old_class:
        return
    new_class = class_editor.copy_class(old_class)
    dialog = class_editor.create_dialog(new_class, main_window.get())
    widget = dialog._widget
    text = QCoreApplication.translate("ClassEditor", "Copy Class")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget, new_class)
        class_editor.signals.new_class_created.emit(new_class)
        class_editor.signals.dialog_accepted.emit(dialog)
    else:
        class_editor.signals.dialog_declined.emit(dialog)
    class_editor.unregister_widget(widget)


def group_classes(
    bsdd_classes: list[BsddClass],
    class_editor: Type[tool.ClassEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
    class_tree: Type[tool.ClassTreeView],
):
    new_class = BsddClass(Code="GroupCode", Name="GroupName", ClassType="Class")
    parent = cl_utils.shared_parent(bsdd_classes, dictionary=project.get(), mode="lowest")
    parent_code = None if parent is None else parent.Code
    new_class.ParentClassCode = parent_code
    dialog = class_editor.create_dialog(new_class, main_window.get())
    widget = dialog._widget
    text = QCoreApplication.translate("ClassEditor", "Group Classes")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_editor.sync_to_model(widget, new_class)
        class_editor.signals.new_class_created.emit(new_class)
        for child_class in bsdd_classes:
            class_tree.move_class(child_class, new_class, project.get())
        class_editor.signals.dialog_accepted.emit(dialog)
    else:
        class_editor.signals.dialog_declined.emit(dialog)


