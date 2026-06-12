from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Type

import qtawesome as qta
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QLineEdit, QPlainTextEdit, QTextEdit

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_menu_actions(
    undo: Type[tool.Undo], main_window: Type[tool.MainWindowWidget]
) -> None:
    from bsdd_gui.module.undo import trigger

    undo_action = main_window.add_action(
        "menuEdit", "Undo", trigger.undo_requested, qta.icon("mdi6.undo"), shortcut="Ctrl+Z"
    )
    redo_action = main_window.add_action(
        "menuEdit", "Redo", trigger.redo_requested, qta.icon("mdi6.redo")
    )
    redo_action.setShortcuts(["Ctrl+Y", "Ctrl+Shift+Z"])
    undo.set_action("undo", undo_action)
    undo.set_action("redo", redo_action)
    update_action_states(undo)


def retranslate_ui(undo: Type[tool.Undo]) -> None:
    undo_action = undo.get_action("undo")
    if undo_action:
        undo_action.setText(QCoreApplication.translate("Undo", "Undo"))
    redo_action = undo.get_action("redo")
    if redo_action:
        redo_action.setText(QCoreApplication.translate("Undo", "Redo"))


def update_action_states(undo: Type[tool.Undo]) -> None:
    undo_action = undo.get_action("undo")
    if undo_action:
        undo_action.setEnabled(undo.can_undo())
    redo_action = undo.get_action("redo")
    if redo_action:
        redo_action.setEnabled(undo.can_redo())


def project_changed(undo: Type[tool.Undo], project: Type[tool.Project]) -> None:
    """New/loaded project becomes the new baseline -- unless we caused it ourselves."""
    if undo.is_restoring():
        return
    bsdd_dictionary = project.get()
    undo.reset(undo.serialize(bsdd_dictionary) if bsdd_dictionary else None)


def changed(undo: Type[tool.Undo], project: Type[tool.Project]) -> None:
    """Some part of the model reported a mutation; checkpoint after a quiet period."""
    if undo.is_restoring():
        return
    undo.schedule_checkpoint()


def flush(undo: Type[tool.Undo], project: Type[tool.Project]) -> None:
    """Take a checkpoint right now if the model differs from the last known state."""
    if undo.is_restoring():
        return
    bsdd_dictionary = project.get()
    if bsdd_dictionary is None:
        return
    undo.checkpoint_if_changed(undo.serialize(bsdd_dictionary))


def perform_undo(
    undo: Type[tool.Undo],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
    class_tree: Type[tool.ClassTreeView],
    pset_table: Type[tool.PropertySetTableView],
) -> None:
    # Focused text inputs keep their own character-level undo.
    focus = QApplication.focusWidget()
    if isinstance(focus, (QLineEdit, QTextEdit, QPlainTextEdit)):
        focus.undo()
        return
    flush(undo, project)
    if not undo.can_undo():
        return
    current = undo.serialize(project.get())
    _restore(undo.pop_undo(current), undo, project, main_window, class_tree, pset_table)


def perform_redo(
    undo: Type[tool.Undo],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
    class_tree: Type[tool.ClassTreeView],
    pset_table: Type[tool.PropertySetTableView],
) -> None:
    focus = QApplication.focusWidget()
    if isinstance(focus, (QLineEdit, QTextEdit, QPlainTextEdit)):
        focus.redo()
        return
    flush(undo, project)
    if not undo.can_redo():
        return
    current = undo.serialize(project.get())
    _restore(undo.pop_redo(current), undo, project, main_window, class_tree, pset_table)


def _restore(
    state: str,
    undo: Type[tool.Undo],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
    class_tree: Type[tool.ClassTreeView],
    pset_table: Type[tool.PropertySetTableView],
) -> None:
    logging.info("Restoring project state from undo history")
    window = main_window.get()
    tree_view = main_window.get_class_view() if window else None
    pset_view = main_window.get_pset_view() if window else None
    active_class = main_window.get_active_class()
    active_code = active_class.Code if active_class else None
    active_pset = main_window.get_active_pset()
    expanded_codes = class_tree.get_expanded_codes(tree_view) if tree_view else set()
    undo.set_restoring(True)
    try:
        new_dictionary = undo.deserialize(state)
        project.get_properties().project_dictionary = new_dictionary
        bsdd_gui.on_new_project()
        if tree_view:
            class_tree.expand_codes(expanded_codes, tree_view)
        if active_code:
            new_active = next((c for c in new_dictionary.Classes if c.Code == active_code), None)
            if new_active is not None:
                # Re-select through the view so dependent views re-enable normally.
                if not class_tree.select_and_expand(new_active, tree_view):
                    main_window.set_active_class(new_active)
                if active_pset and pset_view:
                    row = pset_table.get_row_by_name(pset_view, active_pset)
                    if row is not None:
                        pset_table.select_row(pset_view, row)
    finally:
        undo.set_restoring(False)
    update_action_states(undo)
