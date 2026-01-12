from __future__ import annotations
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt
from typing import Type, TYPE_CHECKING
import bsdd_gui
import logging
import qtawesome as qta

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_window(application: QApplication, main_window: Type[tool.MainWindowWidget]):
    """
    Creates the main window from the given application and hides the console.
    :param application:
    :param main_window:
    :return:
    """
    mw = main_window.create(application)
    mw.show()
    main_window.hide_console()
    main_window.install_validation_styles(application)
    toggle_console_action = main_window.add_action(
        "menuEdit", "ToggleConsole", main_window.signals.toggle_console_requested.emit
    )
    main_window.set_action(mw, "toggle_console", toggle_console_action)
    plus_icon = "mdi6.plus"
    mw.button_classes_add.setIcon(qta.icon(plus_icon))
    mw.button_property_add.setIcon(qta.icon(plus_icon))
    mw.button_Pset_add.setIcon(qta.icon(plus_icon))
    mw.button_search.setIcon(qta.icon("mdi6.magnify"))


def connect_main_window(
    main_window: Type[tool.MainWindowWidget],
    class_tree: Type[tool.ClassTreeView],
    util: Type[tool.Util],
    project: Type[tool.Project],
):
    main_window.signals.active_class_changed.connect(
        lambda c: main_window.set_class_text(c.Name if c is not None else "")
    )
    main_window.signals.active_pset_changed.connect(main_window.set_pset_text)
    main_window.signals.active_property_changed.connect(
        lambda p: main_window.set_property_text(p.Code if p is not None else "")
    )
    signals = main_window.signals
    ui = main_window.get()
    ui.button_classes_add.clicked.connect(signals.new_class_requested.emit)
    ui.button_Pset_add.clicked.connect(signals.new_property_set_requested.emit)
    ui.button_property_add.clicked.connect(signals.new_property_requested.emit)

    ui.button_search.clicked.connect(
        lambda _: class_tree.request_search(main_window.get_class_view())
    )
    main_window.connect_internal_signals()


def retranslate_ui(main_window: Type[tool.MainWindowWidget]):
    main_window.get().retranslateUi(main_window.get())
    main_window.get().setWindowTitle(f"bSDD-Toolkit v{bsdd_gui.__version__}")
    action = main_window.get_action(main_window.get(), "toggle_console")

    if main_window.is_console_visible():
        action.setText(QCoreApplication.translate("MainWindow", "Hide Console"))
        action.setIcon(qta.icon("mdi6.eye-off"))
    else:
        action.setText(QCoreApplication.translate("MainWindow", "Show Console"))
        action.setIcon(qta.icon("mdi6.eye"))


def refresh_status_bar(main_window: Type[tool.MainWindowWidget], project: Type[tool.Project]):
    """bl
    refresh Statusbar-Text and Window-Title
    :param main_window_tool:
    :param project_tool:
    :return:
    """
    bsdd_dictionary = project.get()
    version = f'{QCoreApplication.translate("MainWindow", "Version")}: {bsdd_dictionary.DictionaryVersion}'
    status = " | ".join(
        [
            bsdd_dictionary.OrganizationCode or "",
            bsdd_dictionary.DictionaryCode or "",
            bsdd_dictionary.DictionaryName or "",
            version or "",
        ]
    )
    main_window.set_status_bar_text(status)


def toggle_console(main_window: Type[tool.MainWindowWidget]):
    main_window.toggle_console()


def close_event(
    event,
    file_lock: Type[tool.FileLock],
    project: Type[tool.Project],
    util: Type[tool.Util],
    popups: Type[tool.Popups],
):
    bsdd_dict = project.get()
    last_save = project.get_last_save()
    if bsdd_dict != last_save:
        reply = popups.request_save_before_exit()
        if reply is None:
            # Dont Close Window
            event.ignore()
            return
        if reply:
            project.request_save_as()
        else:
            file_path = util.create_tempfile("_bsdd.json", add_timestamp=True)
            bsdd_dict.save(file_path)
            logging.info(f"File was saved before closing to: '{file_path}'")
    file_lock.unlock_file()
    event.accept()
