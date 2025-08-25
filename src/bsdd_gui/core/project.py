from __future__ import annotations
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from typing import Type, TYPE_CHECKING
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui import tool


import logging

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_project(project: Type[tool.Project]):
    logging.debug(f"Create Project")
    project.create_project()


def open_project(path, project: Type[tool.Project]):
    proj = project.load_project(path)
    bsdd_gui.on_new_project()
    return proj


def create_main_menu_actions(project: Type[tool.Project], main_window: Type[tool.MainWindow]):
    from bsdd_gui.module.project import trigger

    mw_ui = main_window.get()
    action = main_window.add_action("menuFile", "new", trigger.new_clicked)
    project.set_action(mw_ui, "new", action)

    action = main_window.add_action("menuFile", "open_project", trigger.open_clicked)
    project.set_action(mw_ui, "open_project", action)

    action = main_window.add_action("menuFile", "add_project", trigger.add_clicked)
    project.set_action(mw_ui, "add_project", action)

    action = main_window.add_action("menuFile", "save_project", trigger.save_clicked)
    project.set_action(mw_ui, "save_project", action)

    action = main_window.add_action("menuFile", "save_as_clicked", trigger.save_as_clicked)
    project.set_action(mw_ui, "save_as_clicked", action)


def retranslate_ui(project: Type[tool.Project], main_window: Type[tool.MainWindow]):
    mw_ui = main_window.get()

    action = project.get_action(mw_ui, "new")
    action.setText(QCoreApplication.translate("Project", "New"))

    action = project.get_action(mw_ui, "open_project")
    action.setText(QCoreApplication.translate("Project", "Open"))

    action = project.get_action(mw_ui, "add_project")
    action.setText(QCoreApplication.translate("Project", "Add Project"))

    action = project.get_action(mw_ui, "save_project")
    action.setText(QCoreApplication.translate("Project", "Save"))

    action = project.get_action(mw_ui, "save_as_clicked")
    action.setText(QCoreApplication.translate("Project", "Save As ..."))

    # TODO
    # widget = project.get_settings_path_widget()
    # if widget:
    #     widget.ui.retranslateUi(widget)

    # widget = project.get_settings_general_widget()
    # if widget:
    #     widget.ui.retranslateUi(widget)


def new_file_clicked(project: Type[tool.Project], dictionary_editor: Type[tool.DictionaryEditor]):
    widget = dictionary_editor.create_widget()
    widget.show()
    pass
