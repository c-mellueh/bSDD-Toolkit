from __future__ import annotations
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QWidget, QTreeView
from typing import TYPE_CHECKING, Type
from bsdd_gui.module.property_table import ui, models
from bsdd_parser import BsddProperty, BsddClass
from bsdd_parser.utils import bsdd_class as cl_utils

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_menu_actions(
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
    property_editor: Type[tool.PropertyEditor],
) -> None:
    action = main_window.add_action(
        "menuModels",
        "bSDD Properties",
        lambda: property_table.request_widget(None, main_window.get()),
    )
    property_table.set_action(main_window.get(), "open_window", action)


def connect_signals(
    property_table: Type[tool.PropertyTable],
    property_editor: Type[tool.PropertyEditor],
    main_window: Type[tool.MainWindow],
    class_tree: Type[tool.ClassTree],
    project: Type[tool.Project],
):
    property_table.signaller.property_info_requested.connect(property_editor.request_widget)
    property_table.signaller.new_property_requested.connect(property_editor.request_new_property)
    project.signaller.property_added.connect(lambda _: property_table.reset_views())
    property_table.signaller.bsdd_class_double_clicked.connect(
        lambda c: class_tree.select_and_expand(c, main_window.get_class_view())
    )
    property_table.signaller.bsdd_class_double_clicked.connect(
        lambda c: main_window.get().activateWindow()
    )
    property_table.connect_internal_signals()


def retranslate_ui(
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
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
    property_table: Type[tool.PropertyTable],
    util: Type[tool.Util],
    main_window: Type[tool.MainWindow],
):
    widget = property_table.create_widget()
    widget.show()

    def handle_current_changed(current, prv):
        if not current.isValid():
            return
        index = widget.tv_properties.model().mapToSource(current)
        bsdd_property = index.internalPointer()
        property_table.set_active_property(bsdd_property)

    widget.tv_properties.selectionModel().currentChanged.connect(handle_current_changed)

    util.add_shortcut(
        "Ctrl+F",
        widget.tv_properties,
        lambda: property_table.signaller.search_requested.emit(widget.tv_properties),
    )
    retranslate_ui(property_table, main_window, util)


def register_widget(widget: ui.PropertyWidget, property_table: Type[tool.PropertyTable]):
    property_table.register_view(widget)
    property_table.register_view(widget.tv_properties)
    property_table.register_view(widget.tv_classes)
    property_table.connect_widget_to_internal_signals(widget)

    proxy_model = property_table.create_property_model()
    source_model = proxy_model.sourceModel()
    property_table.add_column_to_table(source_model, "Code", lambda p: p.Code)
    property_table.add_column_to_table(source_model, "Datatype", lambda p: p.DataType)
    widget.tv_properties.setModel(proxy_model)

    proxy_model = property_table.create_class_model()
    source_model = proxy_model.sourceModel()
    property_table.add_column_to_table(source_model, "Code", lambda c: c.Code)
    property_table.add_column_to_table(source_model, "Name", lambda c: c.Name)
    widget.tv_classes.setModel(proxy_model)

    property_table.add_context_menu_entry(
        widget.tv_properties,
        lambda: QCoreApplication.translate("PropertySet", "Delete"),
        lambda: property_table.signaller.delete_selection_requested.emit(widget.tv_properties),
        True,
        True,
        True,
    )

    property_table.add_context_menu_entry(
        widget.tv_classes,
        lambda: QCoreApplication.translate("PropertySet", "Delete Properties"),
        lambda: property_table.signaller.delete_selection_requested.emit(widget.tv_classes),
        True,
        True,
        True,
    )


def unregister_widget(
    widget: ui.PropertyWidget,
    property_table: Type[tool.PropertyTable],
):
    property_table.unregister_widget(widget)
    property_table.unregister_widget(widget.tv_properties)
    property_table.unregister_widget(widget.tv_classes)


def search_property(
    view: QTreeView,
    property_table: Type[tool.PropertyTable],
    search: Type[tool.Search],
    project: Type[tool.Project],
):
    bsdd_properties = project.get().Properties
    bsdd_property = search.search_property(bsdd_properties)
    if not bsdd_property:
        return
    # Select the found property in the view and scroll to it
    property_table.select_property(bsdd_property, view)


def create_context_menu(view: QTreeView, pos, property_table: Type[tool.PropertyTable]):
    selected_elements = property_table.get_selected(view)
    menu = property_table.create_context_menu(view, selected_elements)
    if not menu:
        return
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def delete_selection(
    view: QTreeView, property_table: Type[tool.PropertyTable], project: Type[tool.Project]
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
                    project.signaller.property_removed.emit(bsdd_class_property)
    property_table.reset_view(view)
