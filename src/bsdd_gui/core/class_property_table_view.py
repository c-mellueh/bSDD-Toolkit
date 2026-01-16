from __future__ import annotations
from PySide6.QtWidgets import QApplication, QTableView
from typing import Type, TYPE_CHECKING
from PySide6.QtCore import QModelIndex, QCoreApplication, QPoint
from bsdd_json.utils import property_utils as prop_utils
import qtawesome as qta
from bsdd_gui.module.util.constants import CLASS_PROP_CLIPBOARD_KIND
import json

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_property_table_view import ui, models
from bsdd_json import BsddClass, BsddClassProperty, BsddProperty


def connect_signals(
    class_property_table: Type[tool.ClassPropertyTableView],
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    class_property_table.connect_internal_signals()
    class_property_editor.signals.new_class_property_created.connect(
        lambda p: class_property_table.add_class_property(p, main_window.get_active_class())
    )
    class_property_table.signals.item_added.connect(project.signals.class_property_added.emit)
    class_property_table.signals.item_removed.connect(project.signals.class_property_removed.emit)


def rentranslate_ui(property_table: Type[tool.ClassPropertyTableView]):
    pass


def register_view(view: ui.ClassPropertyTable, property_table: Type[tool.ClassPropertyTableView]):
    property_table.register_view(view)


def add_columns_to_view(
    view: ui.ClassPropertyTable,
    property_table: Type[tool.ClassPropertyTableView],
    project: Type[tool.Project],
):

    sort_model, model = property_table.create_model(None)
    property_table.add_column_to_table(
        model, "Name", lambda p: prop_utils.get_name(p, project.get())
    )
    property_table.add_column_to_table(model, "Code", lambda a: a.Code)
    property_table.add_column_to_table(
        model, "Datatype", lambda p: prop_utils.get_datatype(p, project.get())
    )
    property_table.add_column_to_table(model, "Unit", prop_utils.get_units)
    property_table.add_column_to_table(model, "Values", property_table.get_allowed_values)
    property_table.add_column_to_table(model, "Is Required", lambda a: a.IsRequired)
    view.setModel(sort_model)


def add_context_menu_to_view(
    view: ui.ClassPropertyTable, property_table: Type[tool.ClassPropertyTableView]
):
    property_table.clear_context_menu_list(view)
    property_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("ClassPropertyTable", "Delete"),
        lambda: property_table.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.delete"),
        shortcut="Del",
    )
    property_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("ClassPropertyTable", "Edit"),
        lambda: property_table.request_info(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.rename"),
    )

    property_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertyTable", "New"),
        lambda: property_table.request_new_property(),
        False,
        True,
        True,
        icon=qta.icon("mdi6.plus"),
        shortcut="Ctrl+N",
    )

    property_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("ClassPropertyTable", "Copy"),
        lambda: property_table.request_copy(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.content-copy"),
        shortcut="Ctrl+C",
    )
    property_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("PropertyTable", "Paste"),
        lambda: property_table.request_paste(view),
        False,
        True,
        True,
        icon=qta.icon("mdi6.content-paste"),
        shortcut="Ctrl+V",
    )


def create_context_menu(
    view: ui.ClassPropertyTable, pos: QPoint, property_table: Type[tool.ClassPropertyTableView]
):
    bsdd_allowed_values = property_table.get_selected(view)
    menu = property_table.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def connect_view(
    view: ui.ClassPropertyTable,
    property_table: Type[tool.ClassPropertyTableView],
    util: Type[tool.Util],
):
    property_table.connect_view_signals(view)
    util.add_shortcut(
        "Ctrl+N",
        view,
        lambda: property_table.request_new_property(),
    )
    util.add_shortcut(
        "Ctrl+C",
        view,
        lambda: property_table.request_copy(view),
    )
    util.add_shortcut(
        "Ctrl+V",
        view,
        lambda: property_table.request_paste(view),
    )


def reset_views(property_table: Type[tool.ClassPropertyTableView], project: Type[tool.Project]):
    for view in property_table.get_widgets():
        property_table.reset_view(view)


def connect_to_main_window(
    property_table: Type[tool.ClassPropertyTableView], main_window: Type[tool.MainWindowWidget]
):

    def reset_property(new_pset_name: str):
        """
        if the class changes this function checks if the new class has a propertySet with the same name as the old class and selects it
        """
        active_prop = main_window.get_active_property()
        if active_prop is None:
            return
        active_class = main_window.get_active_class()
        property_list = property_table.filter_properties_by_pset(active_class, new_pset_name)
        code_dict = {p.Code: p for p in property_list}
        if active_prop.Code in code_dict:
            new_property = code_dict[active_prop.Code]
            row_index = property_table.get_row_of_property(property_view, new_property)
        else:
            row_index = 0
        property_table.select_row(property_view, row_index or 0)

    property_view = main_window.get_property_view()

    property_table.signals.selection_changed.connect(
        lambda v, n: (main_window.set_active_property(n) if v == property_view else None)
    )
    main_window.signals.active_pset_changed.connect(
        lambda c: property_table.reset_view(property_view)
    )
    main_window.signals.active_pset_changed.connect(reset_property)


def reset_models(
    property_table: Type[tool.ClassPropertyTableView],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
):
    for model in property_table.get_models():
        model.bsdd_data = project.get()
    main_window.set_active_property(None)

    property_table.reset_views()


def copy_property_to_clipboard(
    view: ui.ClassPropertyTable, class_property_table: Type[tool.ClassPropertyTableView]
):
    selected_properties: list[BsddClassProperty] = class_property_table.get_selected(view)
    if not selected_properties:
        return

    seen_property_codes = list()
    properties = []
    class_properties = list()
    for class_property in selected_properties:
        internal_prop = prop_utils.get_internal_property(class_property=class_property)
        if internal_prop:
            if internal_prop.Code not in seen_property_codes:
                properties.append(internal_prop.model_dump(mode="json"))
                seen_property_codes.append(internal_prop.Code)
        class_properties.append(class_property.model_dump(mode="json"))
    if not properties:
        return
    payload = {
        "kind": CLASS_PROP_CLIPBOARD_KIND,
        "class_properties": class_properties,
        "properties": properties,
    }

    QApplication.clipboard().setText(json.dumps(payload, ensure_ascii=False))


def paste_property_from_clipboard(
    view: ui.ClassPropertyTable,
    class_property_table: Type[tool.ClassPropertyTableView],
    property_table: Type[tool.PropertyTableWidget],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    bsdd_dictionary = project.get()
    clipboard_text = QApplication.clipboard().text()
    try:
        payload = json.loads(clipboard_text)
    except:
        return

    if not isinstance(payload, dict) or payload.get("kind") != CLASS_PROP_CLIPBOARD_KIND:
        return

    model: models.ClassPropertyTableModel = view.model().sourceModel()
    bsdd_class_properties = payload.get("class_properties", [])
    properties: list[BsddProperty] = payload.get("properties", [])

    if not isinstance(bsdd_class_properties, list):
        return

    existing_codes = [cp.Code for cp in model.active_class.ClassProperties]
    for bsdd_class_property in bsdd_class_properties:
        if not isinstance(bsdd_class_property, dict):
            continue

        code = bsdd_class_property.get("Code", "New-Class-Property")
        code = util.get_unique_name(code, existing_codes, True)
        bsdd_class_property["Code"] = code
        new_property = BsddClassProperty.model_validate(bsdd_class_property)
        class_property_table.add_class_property(new_property, model.active_class)
        existing_codes.append(code)

    existing_property_codes = [p.Code for p in project.get().Properties]
    for bsdd_property in properties:
        if bsdd_property.get("Code") in existing_property_codes:
            continue
        try:
            new_property = BsddProperty.model_validate(bsdd_property)
            property_table.add_property_to_dictionary(new_property, bsdd_dictionary)
            existing_property_codes.append(new_property.Code)
        except:
            pass
