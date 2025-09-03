from __future__ import annotations
from PySide6.QtCore import QCoreApplication, Qt, QPoint
from PySide6.QtWidgets import QWidget, QTreeView
from typing import TYPE_CHECKING, Type
from bsdd_gui.module.property_table_widget import views, ui, models
from bsdd_json import BsddProperty, BsddClass
from bsdd_json.utils import bsdd_class as cl_utils

if TYPE_CHECKING:
    from bsdd_gui import tool


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
    property_table.connect_internal_signals()


def retranslate_ui(
    property_table: Type[tool.PropertyTableWidget],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    """Retranslates the UI elements of dictionary Editor. and the Actions."""
    action = property_table.get_action(main_window.get(), "open_window")
    text = QCoreApplication.translate("PropertyTable", "Properties Data")
    action.setText(text)
    title = util.get_window_title(QCoreApplication.translate("PropertyTable", "Properties Data"))
    for widget in property_table.get_widgets():
        widget.setWindowTitle(title)


def create_widget(
    parent: QWidget,
    property_table: Type[tool.PropertyTableWidget],
    util: Type[tool.Util],
    main_window: Type[tool.MainWindowWidget],
):
    if property_table.get_widgets():
        widget = list(property_table.get_widgets())[-1]
    else:
        widget = property_table.create_widget(None)

    widget.setParent(parent)
    widget.show()
    widget.activateWindow()
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


def add_columns_to_view(
    view: views.PropertyTable | views.ClassTable,
    property_table: Type[tool.PropertyTableWidget],
):

    if isinstance(view, views.PropertyTable):
        proxy_model, model = property_table.create_property_model()
        model = proxy_model.sourceModel()
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
            lambda: QCoreApplication.translate("PropertySet", "Delete"),
            lambda: property_table.request_delete_selection(view),
            True,
            True,
            True,
        )
    else:
        property_table.add_context_menu_entry(
            view,
            lambda: QCoreApplication.translate("PropertySet", "Delete Properties"),
            lambda: property_table.request_delete_selection(view),
            True,
            True,
            True,
        )


def connect_view(
    view: views.PropertyTable | views.ClassTable,
    property_table: Type[tool.PropertyTableWidget],
    util: Type[tool.Util],
):
    property_table.connect_view_signals(view)
    if isinstance(view, views.PropertyTable):
        util.add_shortcut(
            "Ctrl+F",
            view,
            lambda: property_table.signals.search_requested.emit(view),
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


def connect_to_main_menu(
    property_table: Type[tool.PropertyTableWidget],
    main_window: Type[tool.MainWindowWidget],
) -> None:
    action = main_window.add_action(
        "menuData",
        "bSDD Properties",
        lambda: property_table.request_widget(None, main_window.get()),
    )
    property_table.set_action(main_window.get(), "open_window", action)


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


def delete_selection(
    view: QTreeView, property_table: Type[tool.PropertyTableWidget], project: Type[tool.Project]
):
    selected_elements = property_table.get_selected(view)
    if not selected_elements:
        return
    bsdd_dictionary = project.get()
    if isinstance(selected_elements[0], BsddProperty):
        for bsdd_property in selected_elements:
            bsdd_dictionary.Properties.remove(bsdd_property)
    elif isinstance(selected_elements[0], BsddClass):
        selected_elements: list[BsddClass]
        active_prop = property_table.get_active_property()
        for cl in selected_elements:
            for bsdd_class_property in list(cl.ClassProperties):
                if bsdd_class_property.PropertyCode == active_prop.Code:
                    cl.ClassProperties.remove(bsdd_class_property)
                    project.signals.property_removed.emit(bsdd_class_property)
    property_table.reset_view(view)
