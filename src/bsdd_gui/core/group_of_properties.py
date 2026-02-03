from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication, Qt, QModelIndex
from PySide6.QtWidgets import QTreeView
import logging
import qtawesome as qta
from bsdd_json.utils import class_utils as cl_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.group_of_properties import ui, views


def connect_to_main_window(
    group_of_properties: Type[tool.GroupOfProperties],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
    class_editor: Type[tool.ClassEditorWidget],
):
    # Action uses the WidgetTool request to allow trigger routing

    action = main_window.add_action(
        None,
        "Groups of Properties",
        lambda: group_of_properties.request_widget(project.get(), main_window.get()),
    )
    group_of_properties.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    group_of_properties: Type[tool.GroupOfProperties], main_window: Type[tool.MainWindowWidget]
):
    action = group_of_properties.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("GroupsOfProperties", "Groups of Properties"))


def connect_signals(
    widget_tool: Type[tool.GroupOfProperties],
    class_view: Type[tool.GopClassView],
    property_view: Type[tool.GopPropertyView],
    class_editor: Type[tool.ClassEditorWidget],
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    project: Type[tool.Project],
):
    def handle_new_request(act, view: views.GopClassView):
        active = class_view.get_selected(view)
        active = cl_utils.get_parent(active[0], project.get()) if active else None
        class_editor.request_new_class(act, active)

    widget_tool.connect_internal_signals()
    class_view.connect_internal_signals()
    property_view.connect_internal_signals()

    class_editor.signals.new_class_created.connect(
        lambda c: class_view.add_class_to_dictionary(c, project.get())
    )
    class_view.signals.item_removed.connect(project.signals.class_removed.emit)
    class_view.signals.item_added.connect(project.signals.class_added.emit)
    class_view.signals.new_class_requested.connect(handle_new_request)
    class_property_editor.signals.new_class_property_created.connect(
        lambda p, c: property_view.add_class_property(p, c)
    )
    property_view.signals.item_added.connect(project.signals.class_property_added.emit)
    property_view.signals.item_removed.connect(project.signals.class_property_removed.emit)


def create_widget(data, parent, widget_tool: Type[tool.GroupOfProperties]):
    widget: ui.GopWidget = widget_tool.show_widget(data, parent)
    widget.tb_search.setIcon(qta.icon("mdi.magnify"))
    widget.pb_new_class.setIcon(qta.icon("mdi.plus"))
    widget.pb_new_prop.setIcon(qta.icon("mdi.plus"))


def register_widget(widget: ui.GopWidget, widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.register_widget(widget)


def connect_widget(
    widget: ui.GopWidget,
    widget_tool: Type[tool.GroupOfProperties],
    gop_class_view: Type[tool.GopClassView],
    gop_prop_view: Type[tool.GopPropertyView],
    class_editor: Type[tool.ClassEditorWidget],
):
    widget_tool.connect_widget_signals(widget)
    widget.pb_new_class.clicked.connect(
        lambda *_, w=widget: gop_class_view.request_new_class(w.tv_class)
    )

    def emit_class_info_requested(index: QModelIndex):
        index = class_view.model().mapToSource(index)
        bsdd_class = index.internalPointer()
        if not bsdd_class:
            return
        class_types = "GroupOfProperties"
        class_editor.signals.edit_class_requested.emit(class_types, bsdd_class)

    class_view = widget.tv_class
    widget.tb_search.clicked.connect(lambda _, v=class_view: gop_class_view.request_search(v))
    class_view.doubleClicked.connect(emit_class_info_requested)
    gop_class_view.signals.selection_changed.connect(
        lambda v, c, w=widget: widget_tool.set_active_class(c)
    )

    prop_view = widget.tv_properties

    gop_prop_view.signals.selection_changed.connect(
        lambda v, n: (widget_tool.set_active_property(n) if v == prop_view else None)
    )

    widget_tool.signals.active_class_changed.connect(lambda c: gop_prop_view.reset_view(prop_view))
    widget_tool.signals.active_class_changed.connect(widget_tool.reset_property)
    widget.pb_new_prop.clicked.connect(lambda: gop_prop_view.request_new_property())
    gop_prop_view.set_allowed_class_types(gop_class_view.get_allowed_class_types())
    
    widget_tool.set_active_class(None)


### Item View


def register_class_view(view: views.GopPropertyView, gop_view: Type[tool.GopClassView]):
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


def register_property_view(view: views.GopPropertyView, gop_view: Type[tool.GopPropertyView]):
    gop_view.register_view(view)


def connect_class_view(view: views.GopPropertyView, gop_view: Type[tool.GopClassView]):
    gop_view.connect_view_signals(view)


def connect_property_view(view: views.GopPropertyView, gop_view: Type[tool.GopPropertyView]):
    gop_view.connect_view_signals(view)


def add_columns_to_class_view(
    view: views.GopPropertyView, gop_view: Type[tool.GopClassView], project: Type[tool.Project]
):
    sort_model, model = gop_view.create_model(project.get())
    gop_view.add_column_to_table(model, "Name", lambda av: av.Name)
    gop_view.add_column_to_table(model, "Code", lambda av: av.Code)
    view.setModel(sort_model)


def create_context_menu(
    view: views.GopClassView, pos, gop_view: Type[tool.GopClassView | tool.GopPropertyView]
):
    bsdd_allowed_values = gop_view.get_selected(view)
    menu = gop_view.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def remove_view(view: views.GopClassView, pos, gop_view: Type[tool.GopClassView]):
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
