from __future__ import annotations
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import QPoint, QCoreApplication, Qt, QModelIndex
from typing import Type, TYPE_CHECKING
import logging
import json
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
import qtawesome as qta
from bsdd_gui.module.class_tree_view.constants import JSON_MIME, CODES_MIME
from bsdd_json.models import BsddClass, BsddDictionary, BsddProperty

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree_view import ui
    from bsdd_gui.module.class_tree_view import models


def connect_signals(
    class_tree: Type[tool.ClassTreeView],
    project: Type[tool.Project],
    class_editor: Type[tool.ClassEditorWidget],
):
    class_tree.connect_internal_signals()
    class_editor.signals.new_class_created.connect(
        lambda c: class_tree.add_class_to_dictionary(c, project.get())
    )

    class_tree.signals.item_removed.connect(project.signals.class_removed.emit)
    class_tree.signals.item_added.connect(project.signals.class_added.emit)


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
    logging.info(f"register View {type(view).__name__} done!")


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
        icon=qta.icon("mdi6.content-copy"),
        shortcut="Ctrl+C",
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
        lambda: QCoreApplication.translate("Class", "Extend All"),
        lambda: class_tree.signals.expand_selection_requested.emit(view),
        True,
        True,
        True,
        icon=qta.icon("mdi6.arrow-expand"),
        shortcut="Ctrl+E",
    )
    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Collapse"),
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
        lambda: QCoreApplication.translate("Class", "Info"),
        lambda: class_editor.request_class_editor(get_first_selection(view)),
        True,
        True,
        False,
        icon=qta.icon("mdi6.information"),
    )

    class_tree.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("Class", "Reset View"),
        lambda: class_tree.signals.model_refresh_requested.emit(),
        False,
        True,
        True,
        icon=qta.icon("mdi6.refresh"),
    )


def connect_view(view: ui.ClassView, class_tree: Type[tool.ClassTreeView]):
    class_tree.connect_view_signals(view)


def connect_to_main_window(
    class_tree: Type[tool.ClassTreeView],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    view = main_window.get_class_view()

    util.add_shortcut(
        "Ctrl+C",
        view,
        lambda: main_window.signals.copy_active_class_requested.emit(),
    )

    util.add_shortcut(
        "Del",
        view,
        lambda: class_tree.signals.delete_selection_requested.emit(view),
    )

    util.add_shortcut(
        "Ctrl+E",
        view,
        view.expandAll,
    )
    util.add_shortcut(
        "Ctrl+Alt+E",
        view,
        view.collapseAll,
    )

    util.add_shortcut(
        "Ctrl+G",
        view,
        lambda: class_tree.signals.group_selection_requested.emit(view),
    )
    util.add_shortcut(
        "Ctrl+F",
        view,
        lambda: class_tree.signals.search_requested.emit(view),
    )

    util.add_shortcut(
        "Ctrl+N",
        view,
        lambda: main_window.signals.new_class_requested.emit(),
    )

    class_tree.signals.selection_changed.connect(
        lambda v, n: (main_window.set_active_class(n) if v == view else None),
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
    bsdd_classes = class_tree.get_selected(view)
    if not bsdd_classes:
        return
    class_editor.request_class_grouping(bsdd_classes)


def copy_selected_class(view: ui.ClassView):
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


def handle_mime_move(
    bsdd_dictionary: BsddDictionary, data, row, parent, class_tree: Type[tool.ClassTreeView]
):
    # destination parent
    model: models.ClassTreeModel = class_tree.get_model(bsdd_dictionary)
    dest_parent = parent.siblingAtColumn(0) if parent.isValid() else QModelIndex()
    dest_parent_node = dest_parent.internalPointer() if dest_parent.isValid() else None

    codes = json.loads(bytes(data.data(CODES_MIME)).decode("utf-8"))
    if not codes:
        return False
    # one-at-a-time move (extend to multi later if needed)
    code = codes[0]
    node = cl_utils.get_class_by_code(model.bsdd_dictionary, code)
    if node is None:
        return False
    # destination row (append)
    dest_parent_index = (
        QModelIndex() if dest_parent_node is None else model._index_for_class(dest_parent_node)
    )
    dest_row = model.rowCount(dest_parent_index) if row == -1 else row
    return class_tree.move_class(node, dest_parent_node, model.bsdd_data, dest_row)


def handle_mime_copy(
    bsdd_dictionary: BsddDictionary,
    data,
    parent,
    class_tree: Type[tool.ClassTreeView],
    util: Type[tool.Util],
    property_table: Type[tool.PropertyTableWidget],
):
    # destination parent
    dest_parent = parent.siblingAtColumn(0) if parent.isValid() else QModelIndex()
    dest_parent_node = dest_parent.internalPointer() if dest_parent.isValid() else None
    payload = class_tree.get_payload_from_data(data)
    if payload is None:
        return
    if payload.get("kind") != "BsddClassTransfer" or "classes" not in payload:
        return

    raw_classes = payload["classes"]
    raw_properties = payload["properties"]
    root_codes = set(payload.get("roots", []))

    # 1) build code -> raw map; compute depth to sort parents before children
    class_code_dict = {
        rc["Code"]: rc for rc in raw_classes if isinstance(rc, dict) and "Code" in rc
    }

    ordered_class_codes = sorted(
        class_code_dict.keys(), key=lambda c, ccd=class_code_dict: class_tree.depth_of(c, ccd)
    )  # parents first

    # 2) conflict-safe code mapping
    old2new = {}

    # 3) create & insert classes (parents first), adjusting codes/parents
    for class_code in ordered_class_codes:
        rc = dict(class_code_dict[class_code])  # copy
        # new code (unique in target)
        new_code = util.get_unique_name(rc["Code"], old2new)
        old2new[rc["Code"]] = new_code
        node = class_tree.create_class_from_mime(
            rc, new_code, old2new, root_codes, dest_parent_node
        )
        if node is None:
            continue
        # insert with proper signals (parent must exist now)
        class_tree.add_class_to_dictionary(node, bsdd_dictionary)

    # 4) Insert Properties
    #
    # that don't exist so far
    new_properties = property_table.get_properties_from_mime_payload(payload, bsdd_dictionary)
    for p in new_properties:
        property_table.add_property_to_dictionary(p, bsdd_dictionary)
    return True
