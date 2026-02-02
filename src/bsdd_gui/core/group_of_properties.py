from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication,Qt
from PySide6.QtWidgets import QTreeView
import logging
import qtawesome as qta
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.group_of_properties import ui, views


def connect_to_main_window(
    group_of_properties: Type[tool.GroupOfProperties],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing

    action = main_window.add_action(
        None,
        "GRoups of Properties",
        lambda: group_of_properties.request_widget(project.get(), main_window.get()),
    )
    group_of_properties.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    group_of_properties: Type[tool.GroupOfProperties], main_window: Type[tool.MainWindowWidget]
):
    action = group_of_properties.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("GroupsOfProperties", "Groups of Properties"))


def connect_signals(widget_tool: Type[tool.GroupOfProperties], gop_view: Type[tool.GopClassView]):
    widget_tool.connect_internal_signals()
    gop_view.connect_internal_signals()


def create_widget(data, parent, widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.show_widget(data, parent)


def register_widget(widget: ui.GopWidget, widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.register_widget(widget)


def connect_widget(widget: ui.GopWidget, widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.connect_widget_signals(widget)


### Item View


def register_view(view: views.ClassView, gop_view: Type[tool.GopClassView]):
    gop_view.register_view(view)
    view.setSelectionBehavior(QTreeView.SelectRows)
    view.setSelectionMode(QTreeView.ExtendedSelection)
    view.setAlternatingRowColors(True)
    view.setDragEnabled(True)
    view.setAcceptDrops(True)
    view.setDropIndicatorShown(True)
    view.setDefaultDropAction(Qt.MoveAction)
    view.setDragDropMode(QTreeView.DragDropMode.DragDrop)  # internal DnD
    logging.info(f"register View {type(view).__name__} done!")


def connect_view(view: views.ClassView, gop_view: Type[tool.GopClassView]):
    gop_view.connect_view_signals(view)


def add_columns_to_view(view: views.ClassView, gop_view: Type[tool.GopClassView],project:Type[tool.Project]):
    sort_model, model = gop_view.create_model(project.get())
    gop_view.add_column_to_table(model, "Name", lambda av: av.Name)
    gop_view.add_column_to_table(model, "Code", lambda av: av.Code)
    view.setModel(sort_model)


def add_context_menu_to_view(view: views.ClassView, class_tree: Type[tool.GopClassView],class_editor:Type[tool.ClassEditorWidget]):
    class_tree.clear_context_menu_list(view)
    def get_first_selection(v: ui.ClassView):
        bsdd_classes = class_tree.get_selected(v)
        return bsdd_classes[0] if bsdd_classes else None

    class_tree.clear_context_menu_list(view)
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Copy"),
        lambda v=view: class_tree.request_copy_selection(v),
        True,
        True,
        True,
        icon=qta.icon("mdi6.content-copy"),
        shortcut="Ctrl+C",
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Paste"),
        lambda v=view: class_tree.request_paste(v),
        False,
        True,
        True,
        icon=qta.icon("mdi6.content-paste"),
        shortcut="Ctrl+V",
    )

    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Delete"),
        lambda: class_tree.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.delete"),
        shortcut="Del",
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Extend Selection"),
        lambda: class_tree.signals.expand_selection_requested.emit(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.arrow-expand"),
        shortcut="Ctrl+E",
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Collapse Selection"),
        lambda: class_tree.signals.collapse_selection_requested.emit(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.arrow-collapse"),
        shortcut="Ctrl+Alt+E",
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Group"),
        lambda: class_tree.signals.group_selection_requested.emit(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.group"),
        shortcut="Ctrl+G",
    )

    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Search"),
        lambda: class_tree.signals.search_requested.emit(view),
        False,
        True,
        True,
        icon=qta.icon("mdi6.magnify"),
        shortcut="Ctrl+F",
    )

    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Reset View"),
        lambda: class_tree.signals.model_refresh_requested.emit(),
        False,
        True,
        True,
        icon=qta.icon("mdi6.refresh"),
        shortcut="Ctrl+R",
    )

    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Edit"),
        lambda: class_editor.request_class_editor(get_first_selection(view)),
        True,
        True,
        False,
        icon=qta.icon("mdi6.rename"),
    )



def create_context_menu(view: views.ClassView, pos, gop_view: Type[tool.GopClassView]):
    bsdd_allowed_values = gop_view.get_selected(view)
    menu = gop_view.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def remove_view(view: views.ClassView, pos, gop_view: Type[tool.GopClassView]):
    gop_view.remove_model(view.model().sourceModel())


def reset_models(
    class_tree: Type[tool.GopClassView],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
):
    for model in class_tree.get_models():
        model.bsdd_data = project.get()
    main_window.set_active_class(None)
    class_tree.reset_views()