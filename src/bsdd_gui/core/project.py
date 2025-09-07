from __future__ import annotations
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt
from typing import Type, TYPE_CHECKING
from bsdd_gui.module.project.constants import FILETYPE, OPEN_PATH, SAVE_PATH
import logging
import bsdd_gui
import os
import json

if TYPE_CHECKING:
    from bsdd_gui import tool


import logging

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_signals(project: Type[tool.Project]):
    project.signals.data_changed.connect(lambda n, v: logging.debug(f"'{n}' changed to '{v}'"))


def create_project(project: Type[tool.Project]):
    logging.debug(f"Create Project")
    bsdd_dictionary = project.create_project()
    project.register_project(bsdd_dictionary)


def open_project(path, project: Type[tool.Project]):
    proj = project.load_project(path)
    bsdd_gui.on_new_project()
    return proj


def create_main_menu_actions(project: Type[tool.Project], main_window: Type[tool.MainWindowWidget]):
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


def retranslate_ui(project: Type[tool.Project], main_window: Type[tool.MainWindowWidget]):
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


def new_file_clicked(
    project: Type[tool.Project],
    dictionary_editor: Type[tool.DictionaryEditorWidget],
    popups: Type[tool.Popups],
    main_window: Type[tool.MainWindowWidget],
):
    def validate():
        if dictionary_editor.all_inputs_are_valid(widget):
            dialog.accept()
        else:
            text = QCoreApplication.translate("Project", "Required Inputs are missing!")
            missing_text = QCoreApplication.translate("Project", "is missing")
            missing_inputs = dictionary_editor.get_invalid_inputs(widget)
            popups.create_warning_popup(
                f" {missing_text}\n".join(missing_inputs) + f" {missing_text}",
                None,
                text,
            )

    dialog = project.create_new_project_widget(main_window.get())

    new_dict = project.create_project()
    widget = dictionary_editor.create_widget(new_dict, dialog)
    name = QCoreApplication.translate("Project", "New Project")
    dialog.setWindowTitle(name)
    dialog._layout.insertWidget(0, widget)
    dialog.new_button.clicked.connect(validate)
    if dialog.exec():
        project.register_project(new_dict)
    dictionary_editor.unregister_widget(widget)


def open_file_clicked(
    project_tool: Type[tool.Project],
    appdata: Type[tool.Appdata],
    main_window: Type[tool.MainWindowWidget],
    popups: Type[tool.Popups],
    plugins: Type[tool.Plugins],
):
    path = appdata.get_path(OPEN_PATH)
    title = QCoreApplication.translate("Project", "Open Project")
    path = popups.get_open_path(FILETYPE, main_window.get(), path, title)
    if not path:
        return

    logging.info("Load Project")
    appdata.set_path(OPEN_PATH, path)
    appdata.set_path(SAVE_PATH, path)
    project_tool.load_project(path)
    bsdd_gui.on_new_project()
    for plugin in plugins.get_available_plugins():
        plugins.on_new_project(plugin)


def save_clicked(
    proejct: Type[tool.Project],
    popups: Type[tool.Popups],
    appdata: Type[tool.Appdata],
    main_window: Type[tool.MainWindowWidget],
):
    save_path = appdata.get_path(SAVE_PATH)
    if not os.path.exists(save_path) or not save_path.endswith("json"):
        save_as_clicked(proejct, popups, appdata, main_window)
    else:
        save_project(save_path, proejct, appdata)


def save_as_clicked(
    project: Type[tool.Project],
    popups: Type[tool.Popups],
    appdata: Type[tool.Appdata],
    main_window: Type[tool.MainWindowWidget],
):
    path = appdata.get_path(SAVE_PATH)
    title = QCoreApplication.translate("Project", "Save Project")
    path = popups.get_save_path(FILETYPE, main_window.get(), path, title)
    if path:
        save_project(path, project, appdata)


def save_project(path: str, project: Type[tool.Project], appdata: Type[tool.Appdata]):
    if not path.endswith(".json"):
        path += ".json"
    for plugin_function in project.get_plugin_save_functions():
        if plugin_function is None:
            continue
        plugin_function()
    bsdd_dictionary = project.get()
    with open(path, "w") as file:
        json.dump(bsdd_dictionary.model_dump(mode="json", exclude_none=True), file)
    appdata.set_path(OPEN_PATH, path)
    appdata.set_path(SAVE_PATH, path)
    logging.info(f"Save Done!")
