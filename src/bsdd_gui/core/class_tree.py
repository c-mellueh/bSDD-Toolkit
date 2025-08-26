from __future__ import annotations
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import QPoint, QCoreApplication
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree import ui
    from bsdd_parser.models import BsddClass


def connect_signals(
    class_tree: Type[tool.ClassTree],
    class_editor: Type[tool.ClassEditor],
):
    def insert_class(new_class: BsddClass):
        class_tree.add_class_to_dictionary(new_class)

    class_tree.connect_signals()
    class_editor.signaller.new_class_created.connect(insert_class)


def connect_view(
    view: ui.ClassView,
    class_tree: Type[tool.ClassTree],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    class_tree.register_widget(view)
    bsdd_dictionary = project.get()

    view.setModel(class_tree.create_model(bsdd_dictionary))
    view.setSelectionBehavior(QTreeView.SelectRows)
    view.setSelectionMode(QTreeView.ExtendedSelection)
    view.setAlternatingRowColors(True)
    sel_model = view.selectionModel()
    sel_model.currentChanged.connect(lambda s, d: class_tree.on_current_changed(view, s, d))
    class_tree.connect_view_signals(view)


def reset_views(class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    for view in class_tree.get_widgets():
        class_tree.reset_view(view)


def connect_to_main_window(
    class_tree: Type[tool.ClassTree], main_window: Type[tool.MainWindow], util: Type[tool.Util]
):
    view = main_window.get_class_view()
    model = view.model().sourceModel()
    class_tree.add_column_to_table(model, "Name", lambda a: a.Name)
    class_tree.add_column_to_table(model, "Code", lambda a: a.Code)
    class_tree.add_column_to_table(model, "Status", lambda a: a.Status)
    class_tree.signaller.selection_changed.connect(
        lambda v, n: (main_window.set_active_class(n) if v == view else None)
    )
    util.add_shortcut(
        "Ctrl+X", view, lambda: class_tree.signaller.delete_selection_requested.emit(view)
    )
    util.add_shortcut(
        "Ctrl+G", view, lambda: class_tree.signaller.group_selection_requested.emit(view)
    )
    util.add_shortcut("Ctrl+F", view, lambda: class_tree.signaller.search_requested.emit(view))
    util.add_shortcut(
        "Ctrl+C", view, lambda: main_window.signaller.copy_active_class_requested.emit()
    )

    util.add_shortcut("Ctrl+N", view, lambda: main_window.signaller.new_class_requested.emit())

    util.add_shortcut("Ctrl+E", view, view.expandAll)


def define_class_tree_context_menu(
    main_window: Type[tool.MainWindow],
    class_tree: Type[tool.ClassTree],
    class_editor: Type[tool.ClassEditor],
):
    def get_first_selection(v: ui.ClassView):
        bsdd_classes = class_tree.get_selected_classes(v)
        return bsdd_classes[0] if bsdd_classes else None

    tree = main_window.get_class_view()
    class_tree.clear_context_menu_list(tree)
    class_tree.add_context_menu_entry(
        tree,
        lambda: QCoreApplication.translate("Class", "Copy"),
        lambda: class_editor.request_class_copy(get_first_selection(tree)),
        True,
        True,
        False,
    )
    class_tree.add_context_menu_entry(
        tree,
        lambda: QCoreApplication.translate("Class", "Delete"),
        lambda: class_tree.signaller.delete_selection_requested.emit(tree),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        tree,
        lambda: QCoreApplication.translate("Class", "Extend"),
        lambda: class_tree.signaller.expand_selection_requested.emit(tree),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        tree,
        lambda: QCoreApplication.translate("Class", "Collapse"),
        lambda: class_tree.signaller.collapse_selection_requested.emit(tree),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        tree,
        lambda: QCoreApplication.translate("Class", "Group"),
        lambda: class_tree.signaller.group_selection_requested.emit(tree),
        True,
        True,
        True,
    )
    class_tree.add_context_menu_entry(
        tree,
        lambda: QCoreApplication.translate("Class", "Info"),
        lambda: class_editor.request_class_editor(get_first_selection(tree)),
        True,
        True,
        False,
    )

    class_tree.add_context_menu_entry(
        tree,
        lambda: QCoreApplication.translate("Class", "Reset View"),
        lambda: class_tree.signaller.model_refresh_requested.emit(),
        False,
        True,
        True,
    )


def create_context_menu(view: ui.ClassView, pos: QPoint, class_tree: Type[tool.ClassTree]):
    bsdd_classes = class_tree.get_selected_classes(view)
    menu = class_tree.create_context_menu(view, bsdd_classes)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def delete_selection(
    view: ui.ClassView, class_tree: Type[tool.ClassTree], popups: Type[tool.Popups]
):

    selected_classes = class_tree.get_selected_classes(view)
    delete_request, recursive_deletion = popups.req_delete_items(
        [c.Name for c in selected_classes], item_type=1
    )
    if not delete_request:
        return
    for bsdd_class in selected_classes:
        class_tree.delete_class(bsdd_class, recursive_deletion)


def copy_selected_class(
    view: ui.ClassView,
):
    pass
