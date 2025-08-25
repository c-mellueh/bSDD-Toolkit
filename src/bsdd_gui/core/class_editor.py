from __future__ import annotations
from PySide6.QtCore import QModelIndex, QCoreApplication
from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClass
import logging
from bsdd_parser.utils import bsdd_class as class_util
from copy import copy as cp

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
        class_editor.signaller.class_info_requested.emit(bsdd_class)

    view = main_window.get_class_view()
    view.doubleClicked.connect(emit_class_info_requested)
    main_window.signaller.new_class_requested.connect(
        lambda: create_new_class(class_editor, main_window)
    )
    main_window.signaller.copy_active_class_requested.connect(
        lambda: create_new_class(class_editor, main_window, mode=1)
    )


def create_new_class(
    class_editor: Type[tool.ClassEditor],
    main_window: Type[tool.MainWindow],
    mode=0,
):
    """_summary_
    mode 0 = create new
    mode 1 = copy selected
    Args:
        class_editor (Type[tool.ClassEditor]): _description_
        main_window (Type[tool.MainWindow]): _description_
        project (Type[tool.Project]): _description_
        model (int, optional): _description_. Defaults to 0.
    """

    def validate():
        if class_editor.all_inputs_are_valid(widget):
            dialog.accept()
        else:
            pass

    active_class = main_window.get_active_class()
    if not active_class:
        new_class = BsddClass(Code="undef", Name="undef", ClassType="Class")
    else:
        # new_class = active_class.model_copy(update={}, deep=True)
        if mode == 0:
            dd = active_class.model_dump(include=["Code", "Name", "ParentClassCode"])
            dd["ClassType"] = "Class"
        if mode == 1:
            dd = active_class.model_dump()
        new_class = BsddClass(**dd)

    widget = class_editor.create_widget(new_class)
    class_editor.sync_from_model(widget)
    dialog = class_editor.create_new_class_dialog(main_window.get())
    dialog._layout.insertWidget(0, widget)
    dialog.new_button.clicked.connect(validate)
    if dialog.exec():
        class_editor.sync_to_model(widget)
        class_editor.signaller.new_class_created.emit(new_class)
    class_editor.unregister_widget(widget)


def open_class_editor(
    bsdd_class: BsddClass, class_editor: Type[tool.ClassEditor], main_window: Type[tool.MainWindow]
):
    def validate():
        if class_editor.all_inputs_are_valid(widget):
            dialog.accept()
        else:
            pass

    logging.info(f"Open Class Editor for {bsdd_class.Code}")
    dialog = class_editor.create_edit_class_dialog(main_window.get())
    widget = class_editor.create_widget(bsdd_class)
    class_editor.sync_from_model(widget)

    dialog._layout.insertWidget(0, widget)
    dialog.new_button.clicked.connect(validate)
    if dialog.exec():
        class_editor.sync_to_model(widget)
    class_editor.unregister_widget(widget)
