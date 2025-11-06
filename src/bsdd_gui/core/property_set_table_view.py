from __future__ import annotations

import json
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_set_table_view.models import PsetTableModel

from bsdd_gui.module.property_set_table_view import ui
from PySide6.QtCore import QCoreApplication, QPoint, QModelIndex
from PySide6.QtWidgets import QApplication, QListView
from pydantic import ValidationError
from bsdd_json.models import BsddClass, BsddClassProperty
from bsdd_json.utils import build_unique_code

PSET_CLIPBOARD_KIND = "BsddPropertySetTransfer"


def connect_signals(property_set_table: Type[tool.PropertySetTableView]):
    property_set_table.connect_internal_signals()


def retranslate_ui(property_set_table: Type[tool.PropertySetTableView]):
    return  # TODO


def register_view(view: ui.PsetTableView, property_set_table: Type[tool.PropertySetTableView]):
    property_set_table.register_view(view)
    view.setSelectionBehavior(QListView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QListView.SelectionMode.SingleSelection)
    # view.setAlternatingRowColors(True) #Colors the Row in the AccentColor...


def add_columns_to_view(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTableView],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):

    def rename_pset(model: PsetTableModel, index: QModelIndex, new_name: str):

        old_name = index.data()
        if old_name == new_name:
            return
        bsdd_class = model.active_class
        new_name = util.get_unique_name(
            new_name, property_set_table.get_pset_names_with_temporary(bsdd_class)
        )
        if property_set_table.is_temporary_pset(bsdd_class, old_name):
            property_set_table.rename_temporary_pset(bsdd_class, old_name, new_name)
        else:
            property_set_table.rename_property_set(bsdd_class, old_name, new_name)
        if (
            main_window.get_active_class() == bsdd_class
            and main_window.get_active_pset() == old_name
        ):
            main_window.set_active_pset(new_name)

    bsdd_dictionary = project.get()
    proxy_model, model = property_set_table.create_model(bsdd_dictionary)
    view.setModel(proxy_model)
    property_set_table.add_column_to_table(model, "Name", lambda a: a, rename_pset)


def copy_property_sets_to_clipboard(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTableView],
    main_window: Type[tool.MainWindowWidget],
):
    bsdd_class = main_window.get_active_class()
    if bsdd_class is None:
        return
    selected_psets = property_set_table.get_selected(view)
    if not selected_psets:
        return

    def row_key(name: str):
        row = property_set_table.get_row_by_name(view, name)
        return row if row is not None else float("inf")

    items: list[dict[str, object]] = []
    for pset_name in sorted(selected_psets, key=row_key):
        is_temporary = property_set_table.is_temporary_pset(bsdd_class, pset_name)
        properties = []
        if not is_temporary:
            properties = [
                cp.model_dump(mode="json")
                for cp in bsdd_class.ClassProperties
                if cp.PropertySet == pset_name
            ]
        items.append(
            {
                "name": pset_name,
                "temporary": is_temporary,
                "properties": properties,
            }
        )
    if not items:
        return
    payload = {"kind": PSET_CLIPBOARD_KIND, "items": items}
    QApplication.clipboard().setText(json.dumps(payload, ensure_ascii=False))


def paste_property_sets_from_clipboard(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTableView],
    property_table: Type[tool.ClassPropertyTableView],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    bsdd_class = main_window.get_active_class()
    if bsdd_class is None:
        return

    clipboard_text = QApplication.clipboard().text()
    try:
        payload = json.loads(clipboard_text)
    except (TypeError, json.JSONDecodeError):
        return

    if not isinstance(payload, dict) or payload.get("kind") != PSET_CLIPBOARD_KIND:
        return

    items = payload.get("items")
    if not isinstance(items, list):
        return

    existing_psets = property_set_table.get_pset_names_with_temporary(bsdd_class)
    existing_codes = [cp.Code for cp in bsdd_class.ClassProperties]
    appended_psets: list[str] = []
    properties_added = False

    for entry in items:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        temporary = bool(entry.get("temporary", False))
        properties_data = entry.get("properties") or []
        if not isinstance(properties_data, list):
            properties_data = []

        new_name = util.get_unique_name(name, existing_psets)
        existing_psets.append(new_name)
        appended_psets.append(new_name)

        if temporary or not properties_data:
            property_set_table.add_temporary_pset(bsdd_class, new_name)
            continue

        for prop_data in properties_data:
            if not isinstance(prop_data, dict):
                continue
            new_prop = dict(prop_data)
            base_code = new_prop.get("Code") or f"{new_name}_Property"
            new_code = build_unique_code(str(base_code), existing_codes)
            existing_codes.append(new_code)
            new_prop["Code"] = new_code
            new_prop["PropertySet"] = new_name
            try:
                class_property = BsddClassProperty.model_validate(new_prop)
            except ValidationError:
                continue
            property_table.add_class_property(class_property, bsdd_class)
            properties_added = True

    if not appended_psets:
        return

    property_set_table.signals.model_refresh_requested.emit()
    if properties_added:
        property_table.signals.model_refresh_requested.emit()
    last_name = appended_psets[-1]
    main_window.set_active_pset(last_name)
    row_index = property_set_table.get_row_by_name(view, last_name)
    if row_index is not None:
        property_set_table.select_row(view, row_index)


def connect_view(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTableView],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
):

    main_window.signals.active_class_changed.connect(lambda c: property_set_table.reset_view(view))
    property_set_table.connect_view_signals(view)


def connect_to_main_window(
    property_set_table: Type[tool.PropertySetTableView],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
    property_table: Type[tool.ClassPropertyTableView],
):
    def reset_pset(new_class: BsddClass):
        """
        if the class changes this function checks if the new class has a propertySet with the same name as the old class and selects it
        """
        pset = main_window.get_active_pset()
        if pset is None:
            return
        pset_list = property_set_table.get_pset_names_with_temporary(new_class)
        if not pset_list:
            main_window.set_active_pset(None)
            return
        if pset in pset_list:
            row_index = property_set_table.get_row_by_name(pset_view, pset)
        else:
            row_index = 0
        property_set_table.select_row(pset_view, row_index)

    pset_view = main_window.get_pset_view()
    main_window.signals.active_class_changed.connect(reset_pset)
    util.add_shortcut(
        "Ctrl+C",
        pset_view,
        lambda: copy_property_sets_to_clipboard(pset_view, property_set_table, main_window),
    )
    util.add_shortcut(
        "Ctrl+V",
        pset_view,
        lambda: paste_property_sets_from_clipboard(
            pset_view, property_set_table, property_table, main_window, util
        ),
    )
    property_set_table.signals.selection_changed.connect(
        lambda v, n: (main_window.set_active_pset(n) if v == main_window.get_pset_view() else None)
    )
    main_window.signals.new_property_set_requested.connect(
        lambda: property_set_table.request_new_property_set(main_window.get_active_class())
    )


def create_new_property_set(
    bsdd_class: BsddClass,
    property_set_table: Type[tool.PropertySetTableView],
    util: Type[tool.Util],
):
    if not bsdd_class:
        return
    existings_psets = property_set_table.get_pset_names_with_temporary(bsdd_class)
    new_name = util.get_unique_name(
        QCoreApplication.translate("PropertySetTable", "New PropertySet"), existings_psets
    )
    property_set_table.add_temporary_pset(bsdd_class, new_name)
    property_set_table.signals.model_refresh_requested.emit()


def define_context_menu(
    main_window: Type[tool.MainWindowWidget],
    property_set_table: Type[tool.PropertySetTableView],
    util: Type[tool.Util],
    property_table: Type[tool.ClassPropertyTableView],
):

    view = main_window.get_pset_view()
    property_set_table.clear_context_menu_list(view)
    property_set_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertySet", "Copy"),
        lambda: copy_property_sets_to_clipboard(view, property_set_table, main_window),
        True,
        True,
        True,
    )
    property_set_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertySet", "Paste"),
        lambda: paste_property_sets_from_clipboard(
            view, property_set_table, property_table, main_window, util
        ),
        False,
        True,
        True,
    )
    property_set_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertySet", "Delete"),
        lambda: property_set_table.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )

    property_set_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertySet", "Rename"),
        lambda: property_set_table.signals.rename_selection_requested.emit(view),
        True,
        True,
        False,
    )


def create_context_menu(
    view: ui.PsetTableView, pos: QPoint, property_set_table: Type[tool.PropertySetTableView]
):
    selected_psets = property_set_table.get_selected(view)
    menu = property_set_table.create_context_menu(view, selected_psets)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def delete_selection(
    view: ui.PsetTableView,
    property_set_table: Type[tool.PropertySetTableView],
    property_table: Type[tool.ClassPropertyTableView],
    main_window: Type[tool.MainWindowWidget],
):
    """_summary_
    this function seperates between virtual psets and real psets and deletes them accordingly
    Args:
        view (ui.PsetTableView): _description_
        property_set_table (Type[tool.PropertySetTable]): _description_
        property_table (Type[tool.ClassPropertyTable]): _description_
        main_window (Type[tool.MainWindow]): _description_
    """

    bsdd_class = view.model().sourceModel().active_class
    selected_psets = property_set_table.get_selected(view)
    for prop in list(bsdd_class.ClassProperties):
        if prop.PropertySet in selected_psets:
            property_table.remove_property(bsdd_class, prop)
    for pset in selected_psets:
        if property_set_table.is_temporary_pset(bsdd_class, pset):
            property_set_table.remove_temporary_pset(bsdd_class, pset)
        property_set_table.signals.property_set_deleted.emit(bsdd_class, pset)
        if bsdd_class == main_window.get_active_class() and pset == main_window.get_active_pset():
            main_window.set_active_pset(None)
            main_window.set_active_property(None)

    property_table.signals.model_refresh_requested.emit()
    property_set_table.signals.model_refresh_requested.emit()


def reset_models(
    property_table: Type[tool.PropertySetTableView],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
):
    for model in property_table.get_models():
        model.bsdd_data = project.get()
    main_window.set_active_pset(None)
    property_table.reset_views()
