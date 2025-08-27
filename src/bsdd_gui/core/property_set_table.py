from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_set_table.models import PsetTableModel

from bsdd_gui.module.property_set_table import ui
from PySide6.QtCore import QCoreApplication, QPoint, QModelIndex
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
    property_set_table.connect_view_signals(view)


def connect_to_main_window(
    property_set_table: Type[tool.PropertySetTable],
    main_window: Type[tool.MainWindow],
    util: Type[tool.Util],
):
    def reset_pset(new_class: BsddClass):
        """
        if the class changes this function checks if the new class has a propertySet with the same name as the old class and selects it
        """
        pset = main_window.get_active_pset()
        if pset is None:
            return
        pset_list = property_set_table.get_pset_list(new_class)
        if not pset_list:
            main_window.set_active_pset(None)
            return
        if pset in pset_list:
            row_index = property_set_table.get_row_by_name(pset_view, pset)
        else:
            row_index = 0
        property_set_table.select_row(pset_view, row_index)

    def rename_pset(model: PsetTableModel, index: QModelIndex, new_name: str):

        old_name = index.data()
        if old_name == new_name:
            return
        bsdd_class = model.active_class
        new_name = util.get_unique_name(new_name, property_set_table.get_pset_list(bsdd_class))
        if property_set_table.is_temporary_pset(bsdd_class, old_name):
            property_set_table.rename_temporary_pset(bsdd_class, old_name, new_name)
        else:
            property_set_table.rename_property_set(bsdd_class, old_name, new_name)
        if (
            main_window.get_active_class() == bsdd_class
            and main_window.get_active_pset() == old_name
        ):
            main_window.set_active_pset(new_name)

    property_set_table.connect_signals()
    pset_view = main_window.get_pset_view()
    model = pset_view.model().sourceModel()
    pset_view.setEditTriggers(
        pset_view.EditTrigger.DoubleClicked | pset_view.EditTrigger.SelectedClicked
    )

    property_set_table.add_column_to_table(model, "Name", lambda a: a, rename_pset)

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


def define_context_menu(
    main_window: Type[tool.MainWindow], property_set_table: Type[tool.PropertySetTable]
):

    view = main_window.get_pset_view()
    property_set_table.clear_context_menu_list(view)
    property_set_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertySet", "Delete"),
        lambda: property_set_table.signaller.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )

    property_set_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertySet", "Rename"),
        lambda: property_set_table.signaller.rename_selection_requested.emit(view),
        True,
        True,
        False,
    )


def create_context_menu(
    view: ui.PsetTableView, pos: QPoint, property_set_table: Type[tool.PropertySetTable]
):
    selected_psets = property_set_table.get_selected(view)
    menu = property_set_table.create_context_menu(view, selected_psets)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def delete_selection(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTable],
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
):
    bsdd_class = view.model().sourceModel().active_class
    selected_psets = property_set_table.get_selected(view)
    for prop in list(bsdd_class.ClassProperties):
        if prop.PropertySet in selected_psets:
            property_table.remove_property(bsdd_class, prop)
    for pset in selected_psets:
        if property_set_table.is_temporary_pset(bsdd_class, pset):
            property_set_table.remove_temporary_pset(bsdd_class, pset)
        property_set_table.signaller.property_set_deleted.emit(bsdd_class, pset)
        if bsdd_class == main_window.get_active_class() and pset == main_window.get_active_pset():
            main_window.set_active_pset(None)
            main_window.set_active_property(None)

    property_table.signaller.model_refresh_requested.emit()
    property_set_table.signaller.model_refresh_requested.emit()


def rename_selection(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTable],
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
):
    selected_psets = [i for i in view.selectedIndexes() if i.column() == 0][0]
    view.edit(selected_psets)
