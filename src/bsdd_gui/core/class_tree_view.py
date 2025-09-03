from __future__ import annotations
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import QPoint, QCoreApplication, Qt
from typing import Type, TYPE_CHECKING
from bsdd_parser.utils import bsdd_class as class_utils
import logging

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree_view import ui
    from bsdd_parser.models import BsddClass


def connect_signals(class_tree: Type[tool.ClassTreeView], project: Type[tool.Project]):
    class_tree.connect_internal_signals()
    project.signals.class_added.connect(
        lambda c: class_tree.add_class_to_dictionary(c, project.get())
    )
    class_tree.signals.item_deleted.connect(project.signals.class_removed.emit)


def retranslate_ui(class_tree: Type[tool.ClassTreeView]):
    pass


def register_view(view: ui.ClassView, class_tree: Type[tool.ClassTreeView]):
    class_tree.register_view(view)
    view.setSelectionBehavior(QTreeView.SelectRows)
    view.setSelectionMode(QTreeView.ExtendedSelection)
    view.setAlternatingRowColors(True)
    view.setDragEnabled(True)
    view.setAcceptDrops(True)
    view.setDropIndicatorShown(True)
    view.setDefaultDropAction(Qt.MoveAction)
    view.setDragDropMode(QTreeView.DragDropMode.DragDrop)  # internal DnD
    logging.info(f"register View {view} done!")


def add_columns_to_view(
    view: ui.ClassView,
    class_tree: Type[tool.ClassTreeView],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    proxy_model, model = class_tree.create_model(None)
    class_tree.add_column_to_table(model, "Name", lambda a: a.Name)
    class_tree.add_column_to_table(model, "Code", lambda a: a.Code)
    class_tree.add_column_to_table(model, "Status", lambda a: a.Status)
    view.setModel(proxy_model)
    logging.info(f"add columns to view {view} done!")


def add_context_menu_to_view(
    view: ui.ClassView,
    class_tree: Type[tool.ClassTreeView],
    class_editor: Type[tool.ClassEditorWidget],
):
    def get_first_selection(v: ui.ClassView):
        bsdd_classes = class_tree.get_selected(v)
        return bsdd_classes[0] if bsdd_classes else None

    class_tree.clear_context_menu_list(view)
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Copy"),
        lambda: class_editor.request_class_copy(get_first_selection(view)),
        True,
        True,
        False,
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Delete"),
        lambda: class_tree.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Extend"),
        lambda: class_tree.signals.expand_selection_requested.emit(view),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Collapse"),
        lambda: class_tree.signals.collapse_selection_requested.emit(view),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Group"),
        lambda: class_tree.signals.group_selection_requested.emit(view),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Info"),
        lambda: class_editor.request_class_editor(get_first_selection(view)),
        True,
        True,
        False,
    )

    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Reset View"),
        lambda: class_tree.signals.model_refresh_requested.emit(),
        False,
        True,
        True,
    )


def connect_view(view: ui.ClassView, class_tree: Type[tool.ClassTreeView]):
    class_tree.connect_view_signals(view)


def connect_to_main_window(
    class_tree: Type[tool.ClassTreeView],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    view = main_window.get_class_view()
    util.add_shortcut("Del", view, lambda: class_tree.signals.delete_selection_requested.emit(view))
    util.add_shortcut(
        "Ctrl+G", view, lambda: class_tree.signals.group_selection_requested.emit(view)
    )
    util.add_shortcut("Ctrl+F", view, lambda: class_tree.signals.search_requested.emit(view))
    util.add_shortcut(
        "Ctrl+C", view, lambda: main_window.signals.copy_active_class_requested.emit()
    )

    util.add_shortcut("Ctrl+N", view, lambda: main_window.signals.new_class_requested.emit())

    util.add_shortcut("Ctrl+E", view, view.expandAll)
    class_tree.signals.selection_changed.connect(
        lambda v, n: (main_window.set_active_class(n) if v == view else None)
    )


def create_context_menu(view: ui.ClassView, pos: QPoint, class_tree: Type[tool.ClassTreeView]):
    bsdd_classes = class_tree.get_selected(view)
    menu = class_tree.create_context_menu(view, bsdd_classes)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def delete_selection(
    view: ui.ClassView,
    class_tree: Type[tool.ClassTreeView],
    popups: Type[tool.Popups],
    project: Type[tool.Project],
):

    selected_classes = class_tree.get_selected(view)
    delete_request, recursive_deletion = popups.req_delete_items(
        [c.Name for c in selected_classes], item_type=1
    )
    if not delete_request:
        return
    for bsdd_class in selected_classes:
        if recursive_deletion:
            class_tree.delete_class_with_children(bsdd_class, project.get())
        else:
            class_tree.delete_class(bsdd_class, project.get())


def group_selection(
    view: ui.ClassView,
    class_tree: Type[tool.ClassTreeView],
    class_editor: Type[tool.ClassEditorWidget],
):
    bsdd_classes = class_tree.get_selected(
        view,
    )
    if not bsdd_classes:
        return
    class_editor.request_class_grouping(bsdd_classes)


def copy_selected_class(
    view: ui.ClassView,
):
    pass  # TODO


def search_class(
    view: ui.ClassView,
    search: Type[tool.SearchWidget],
    class_tree: Type[tool.ClassTreeView],
    project: Type[tool.Project],
):

    cl = search.search_class(project.get().Classes)
    if not cl:
        return
    class_tree.select_and_expand(cl, view)


def reset_models(
    class_tree: Type[tool.ClassTreeView],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
):
    for model in class_tree.get_models():
        model.bsdd_data = project.get()
    main_window.set_active_class(None)
    class_tree.reset_views()
