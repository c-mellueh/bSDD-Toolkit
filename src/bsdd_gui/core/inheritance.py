from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Type

import qtawesome as qta
from PySide6.QtCore import QCoreApplication

from bsdd_gui.tool.inheritance import SETTING

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_menu_actions(
    inheritance: Type[tool.Inheritance], main_window: Type[tool.MainWindowWidget]
) -> None:
    from bsdd_gui.module.inheritance import trigger

    action = main_window.add_action(
        "menuFile", "Project Settings", trigger.dialog_requested, qta.icon("mdi6.file-cog")
    )
    inheritance.set_action(action)


def retranslate_ui(inheritance: Type[tool.Inheritance]) -> None:
    action = inheritance.get_action()
    if action:
        action.setText(QCoreApplication.translate("Inheritance", "Project Settings"))
    dialog = inheritance.get_dialog()
    if dialog:
        dialog.retranslate_ui()


def project_changed(
    inheritance: Type[tool.Inheritance], project: Type[tool.Project], undo: Type[tool.Undo]
) -> None:
    """New, loaded or restored project: complete it (strict mode) and make it the reference."""
    bsdd_dictionary = project.get()
    if bsdd_dictionary is not None and project.get_setting(SETTING) and not undo.is_restoring():
        added = inheritance.complete(bsdd_dictionary)
        if added:
            logging.info(f"Strict inheritance: added {added} inherited class properties")
        return
    inheritance.remember(bsdd_dictionary)


def changed(
    inheritance: Type[tool.Inheritance], project: Type[tool.Project], undo: Type[tool.Undo]
) -> None:
    if undo.is_restoring() or not project.get_setting(SETTING):
        return
    inheritance.schedule_check()


def check(
    inheritance: Type[tool.Inheritance],
    project: Type[tool.Project],
    undo: Type[tool.Undo],
    popups: Type[tool.Popups],
    main_window: Type[tool.MainWindowWidget],
    class_tree: Type[tool.ClassTreeView],
    pset_table: Type[tool.PropertySetTableView],
    class_property_table: Type[tool.ClassPropertyTableView],
) -> None:
    """Apply the rules to the last edit: pass it on to the children or undo it."""
    bsdd_dictionary = project.get()
    if bsdd_dictionary is None or undo.is_restoring() or not project.get_setting(SETTING):
        return
    if inheritance.is_unchanged(bsdd_dictionary):
        return
    edited = inheritance.serialize(bsdd_dictionary)
    errors = inheritance.apply(bsdd_dictionary)
    if errors:
        from bsdd_gui.core import undo as undo_core

        last_good = inheritance.get_last_good()
        if last_good is not None:
            undo_core.restore_state(last_good, undo, project, main_window, class_tree, pset_table)
        title = QCoreApplication.translate("Inheritance", "Strict inheritance")
        text = QCoreApplication.translate(
            "Inheritance", "The change was undone, it would remove inherited data:"
        )
        popups.create_warning_popup("\n".join(errors), title, text)
        return
    if inheritance.get_last_good() != edited:  # passed on to children / completed
        refresh_views(main_window, pset_table, class_property_table)


def refresh_views(
    main_window: Type[tool.MainWindowWidget],
    pset_table: Type[tool.PropertySetTableView],
    class_property_table: Type[tool.ClassPropertyTableView],
) -> None:
    pset_table.signals.model_refresh_requested.emit()
    class_property_table.signals.model_refresh_requested.emit()
    main_window.signals.update_pset_combobox_requested.emit()


def open_dialog(
    inheritance: Type[tool.Inheritance],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
) -> None:
    dialog = inheritance.create_dialog(main_window.get())
    inheritance.set_toggle_checked(bool(project.get_setting(SETTING)))
    dialog.exec()
    inheritance.set_dialog(None)


def set_strict(
    enabled: bool,
    inheritance: Type[tool.Inheritance],
    project: Type[tool.Project],
    popups: Type[tool.Popups],
    main_window: Type[tool.MainWindowWidget],
    pset_table: Type[tool.PropertySetTableView],
    class_property_table: Type[tool.ClassPropertyTableView],
) -> None:
    bsdd_dictionary = project.get()
    if bsdd_dictionary is None:
        return
    if not enabled:
        project.set_setting(SETTING, False)
        return
    missing = inheritance.missing_count(bsdd_dictionary)
    if missing:
        title = QCoreApplication.translate("Inheritance", "Switch on strict inheritance?")
        text = QCoreApplication.translate(
            "Inheritance",
            "{} class properties are missing in child classes and will be added from their "
            "parent classes.",
        ).format(missing)
        if not popups.request_yes_no(title, text):
            inheritance.set_toggle_checked(False)
            return
    project.set_setting(SETTING, True)
    added = inheritance.complete(bsdd_dictionary)
    if added:
        logging.info(f"Strict inheritance: added {added} inherited class properties")
    refresh_views(main_window, pset_table, class_property_table)
    # let the undo history pick up the added class properties
    project.signals.data_changed.emit("strict_inheritance", True)
