from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
from bsdd_gui.module.property_set_table import ui
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QListView
from bsdd_parser.models import BsddClass


def connect_view(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTable],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindow],
):
    property_set_table.register_widget(view)
    bsdd_dictionary = project.get()
    model = property_set_table.create_model(bsdd_dictionary)
    view.setModel(model)
    view.setSelectionBehavior(QListView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QListView.SelectionMode.SingleSelection)
    view.setAlternatingRowColors(True)
    sel_model = view.selectionModel()
    # sel_model.selectionChanged.connect(lambda s,d: class_tree.on_selection_changed(view,s,d))
    sel_model.currentChanged.connect(lambda s, d: property_set_table.on_current_changed(view, s, d))
    main_window.signaller.active_class_changed.connect(
        lambda c: property_set_table.reset_view(view)
    )


def reset_views(pset_list: Type[tool.PropertySetTable], project: Type[tool.Project]):
    for view in pset_list.get_widgets():
        pset_list.reset_view(view)


def connect_to_main_window(
    property_set_table: Type[tool.PropertySetTable], main_window: Type[tool.MainWindow]
):
    def reset_pset(new_class: BsddClass):
        """
        if the class changes this function checks if the new class has a propertySet with the same name as the old class and selects it
        """
        pset = main_window.get_active_pset()
        if pset is None:
            return
        pset_list = property_set_table.get_pset_list(new_class)
        if pset in pset_list:
            row_index = property_set_table.get_row_by_name(pset_view, pset)
        else:
            row_index = 0
        property_set_table.select_row(pset_view, row_index)

    property_set_table.connect_signals()
    pset_view = main_window.get_pset_view()
    model = pset_view.model().sourceModel()
    property_set_table.add_column_to_table(model, "Name", lambda a: a)
    main_window.signaller.active_class_changed.connect(reset_pset)
    property_set_table.signaller.selection_changed.connect(
        lambda v, n: (main_window.set_active_pset(n) if v == main_window.get_pset_view() else None)
    )
    main_window.signaller.new_property_set_requested.connect(
        lambda: property_set_table.request_new_property_set(main_window.get_active_class())
    )


def create_new_property_set(
    bsdd_class: BsddClass, property_set_table: Type[tool.PropertySetTable], util: Type[tool.Util]
):
    existings_psets = property_set_table.get_pset_list(bsdd_class)
    new_name = util.get_unique_name(
        QCoreApplication.translate("PropertySetTable", "New PropertySet"), existings_psets
    )
    property_set_table.add_temporary_pset(bsdd_class, new_name)
    property_set_table.signaller.model_refresh_requested.emit()


def reset_views(property_set_table: Type[tool.PropertySetTable]):
    for view in property_set_table.get_widgets():
        property_set_table.reset_view(view)
