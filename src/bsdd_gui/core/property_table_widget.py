from __future__ import annotations
import json
from PySide6.QtCore import QCoreApplication, Qt, QPoint
from PySide6.QtWidgets import QWidget, QTreeView, QApplication
from typing import TYPE_CHECKING, Type
from bsdd_gui.module.property_table_widget import views, ui, models
from bsdd_json import BsddProperty, BsddClass, BsddClassProperty
import qtawesome as qta
from bsdd_gui.module.util.constants import PROP_CLIPBOARD_KIND
from pydantic import ValidationError

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_to_main_menu(
    property_table: Type[tool.PropertyTableWidget],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
) -> None:
    action = main_window.add_action(None, "Properties", lambda: property_table.request_widget())
    property_table.set_action(main_window.get(), "open_window", action)


def connect_signals(
    property_table: Type[tool.PropertyTableWidget],
    property_editor: Type[tool.PropertyEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    class_tree: Type[tool.ClassTreeView],
    project: Type[tool.Project],
):
    property_table.signals.property_info_requested.connect(property_editor.request_widget)
    property_table.signals.new_property_requested.connect(property_editor.request_new_property)
    project.signals.property_added.connect(lambda _: property_table.reset_views())
    property_table.signals.bsdd_class_double_clicked.connect(
        lambda c: class_tree.select_and_expand(c, main_window.get_class_view())
    )
    property_table.signals.bsdd_class_double_clicked.connect(
        lambda c: main_window.get().activateWindow()
    )

    def handle_item_remove(item):
        if isinstance(item, BsddProperty):
            project.signals.property_removed.emit(item)
        elif isinstance(item, BsddClassProperty):
            project.signals.class_property_removed.emit(item)

    def handle_item_add(item):
        if isinstance(item, BsddProperty):
            project.signals.property_added.emit(item)
        elif isinstance(item, BsddClassProperty):
            project.signals.class_property_added.emit(item)

    property_editor.signals.new_property_created.connect(
        lambda p: property_table.add_property_to_dictionary(p, project.get())
    )
    property_table.signals.item_added.connect(handle_item_add)
    property_table.signals.item_removed.connect(handle_item_remove)
    property_table.connect_internal_signals()


def retranslate_ui(
    property_table: Type[tool.PropertyTableWidget],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    """Retranslates the UI elements of dictionary Editor. and the Actions."""
    action = property_table.get_action(main_window.get(), "open_window")
    text = QCoreApplication.translate("PropertyTable", "Properties")
    action.setText(text)
    title = util.get_window_title(QCoreApplication.translate("PropertyTable", "bSDD Properties"))
    for widget in property_table.get_widgets():
        widget.setWindowTitle(title)


def create_widget(
    property_table: Type[tool.PropertyTableWidget],
    util: Type[tool.Util],
    main_window: Type[tool.MainWindowWidget],
):
    if property_table.get_widgets():
        widget = property_table.get_widgets()[-1]
    else:
        widget = property_table.create_widget(main_window.get())
    widget: ui.PropertyWidget
    widget.show()
    widget.raise_()
    widget.activateWindow()
    widget.tb_new.setIcon(qta.icon("mdi6.plus"))
    retranslate_ui(property_table, main_window, util)


def register_widget(widget: ui.PropertyWidget, property_table: Type[tool.PropertyTableWidget]):
    property_table.register_widget(widget)


def connect_widget(widget: ui.PropertyWidget, property_table: Type[tool.PropertyTableWidget]):
    property_table.connect_widget_signals(widget)
    widget.closed.connect(lambda w=widget: property_table.unregister_view(w.tv_classes))
    widget.closed.connect(lambda w=widget: property_table.unregister_view(w.tv_properties))


def register_view(
    view: views.PropertyTable | views.ClassTable, property_table: Type[tool.PropertyTableWidget]
):
    property_table.register_view(view)
    # Common selection behavior
    view.setSelectionBehavior(QTreeView.SelectRows)
    view.setSelectionMode(QTreeView.ExtendedSelection)
    view.setAlternatingRowColors(True)
    # Enable drag/drop on the properties table for cross-instance copy
    if isinstance(view, views.PropertyTable):
        view.setDragEnabled(True)
        view.setAcceptDrops(True)
        view.setDropIndicatorShown(True)
        view.setDefaultDropAction(Qt.CopyAction)
        view.setDragDropMode(QTreeView.DragDrop)


def add_columns_to_view(
    view: views.PropertyTable | views.ClassTable, property_table: Type[tool.PropertyTableWidget]
):

    if isinstance(view, views.PropertyTable):
        proxy_model, model = property_table.create_property_model()
        model = proxy_model.sourceModel()
        property_table.add_column_to_table(model, "Name", lambda p: p.Name)
        property_table.add_column_to_table(model, "Code", lambda p: p.Code)
        property_table.add_column_to_table(model, "Datatype", lambda p: p.DataType)
        view.setModel(proxy_model)

    else:
        proxy_model, model = property_table.create_class_model()
        source_model = proxy_model.sourceModel()
        property_table.add_column_to_table(source_model, "Code", lambda c: c.Code)
        property_table.add_column_to_table(source_model, "Name", lambda c: c.Name)
        view.setModel(proxy_model)


def add_context_menu_to_view(
    view: views.PropertyTable | views.ClassTable,
    property_table: Type[tool.PropertyTableWidget],
):

    if isinstance(view, views.PropertyTable):
        property_table.add_context_menu_entry(
            view,
            lambda: QCoreApplication.translate("PropertyTable", "Delete"),
            lambda: property_table.request_delete_selection(view),
            True,
            True,
            True,
            icon=qta.icon("mdi6.delete"),
            shortcut="Del",
        )
        property_table.add_context_menu_entry(
            view,
            lambda: QCoreApplication.translate("PropertyTable", "Search"),
            lambda: property_table.signals.search_requested.emit(view),
            False,
            True,
            True,
            icon=qta.icon("mdi6.magnify"),
            shortcut="Ctrl+F",
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
            lambda: QCoreApplication.translate("PropertyTable", "Copy"),
            lambda: property_table.request_property_copy(view),
            True,
            True,
            True,
            icon=qta.icon("mdi6.content-copy"),
            shortcut="Ctrl+C",
        )
        property_table.add_context_menu_entry(
            view,
            lambda: QCoreApplication.translate("PropertyTable", "Paste"),
            lambda: property_table.request_property_paste(view),
            False,
            True,
            True,
            icon=qta.icon("mdi6.content-paste"),
            shortcut="Ctrl+V",
        )
    else:
        property_table.add_context_menu_entry(
            view,
            lambda: QCoreApplication.translate("PropertyTable", "Delete Properties"),
            lambda: property_table.request_delete_selection(view),
            True,
            True,
            True,
            icon=qta.icon("mdi6.delete"),
            shortcut="Del",
        )


def connect_view(
    view: views.PropertyTable | views.ClassTable,
    property_table: Type[tool.PropertyTableWidget],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    property_table.connect_view_signals(view)

    if isinstance(view, views.PropertyTable):
        util.add_shortcut(
            "Ctrl+F",
            view,
            lambda: property_table.signals.search_requested.emit(view),
        )
        util.add_shortcut(
            "Ctrl+N",
            view,
            lambda: property_table.request_new_property(),
        )
        util.add_shortcut(
            "Ctrl+C",
            view,
            lambda: property_table.request_property_copy(view),
        )
        util.add_shortcut(
            "Ctrl+V",
            view,
            lambda: property_table.request_property_paste(view),
        )

    util.add_shortcut(
        "Del",
        view,
        lambda: property_table.request_delete_selection(view),
    )


def create_context_menu(
    view: views.PropertyTable | views.ClassTable,
    pos: QPoint,
    property_table: Type[tool.PropertyTableWidget],
):
    bsdd_allowed_values = property_table.get_selected(view)
    menu = property_table.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def remove_view(
    view: views.PropertyTable | views.ClassTable, property_table: Type[tool.PropertyTableWidget]
):
    property_table.remove_model(view.model().sourceModel())


def search_property(
    view: QTreeView,
    property_table: Type[tool.PropertyTableWidget],
    search: Type[tool.SearchWidget],
    project: Type[tool.Project],
):
    bsdd_properties = project.get().Properties
    bsdd_property = search.search_property(bsdd_properties)
    if not bsdd_property:
        return
    # Select the found property in the view and scroll to it
    property_table.select_property(bsdd_property, view)


def copy_property_to_clipboard(
    view: views.PropertyTable, property_table: Type[tool.PropertyTableWidget]
):

    selected_properties: list[BsddProperty] = property_table.get_selected(view)
    if not selected_properties:
        return

    properties = []
    for bsdd_property in selected_properties:
        properties = [bsdd_property.model_dump(mode="json")]
    if not properties:
        return
    payload = {"kind": PROP_CLIPBOARD_KIND, "items": properties}
    QApplication.clipboard().setText(json.dumps(payload, ensure_ascii=False))


def paste_property_from_clipboard(
    view: views.PropertyTable,
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

    if not isinstance(payload, dict) or payload.get("kind") != PROP_CLIPBOARD_KIND:
        return

    bsdd_properties = payload.get("items")
    if not isinstance(bsdd_properties, list):
        return

    existing_codes = [p.Code for p in bsdd_dictionary.Properties]
    for bsdd_property in bsdd_properties:
        if not isinstance(bsdd_property, dict):
            continue

        code = bsdd_property.get("Code", "NewProperty")
        code = util.get_unique_name(code, existing_codes, True)
        bsdd_property["Code"] = code
        try:
            new_property = BsddProperty.model_validate(bsdd_property)
            property_table.add_property_to_dictionary(new_property, bsdd_dictionary)
            existing_codes.append(code)
        except ValidationError:
            continue
    property_table.select_property(new_property, view)
