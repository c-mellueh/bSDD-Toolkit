from __future__ import annotations
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from typing import Type, TYPE_CHECKING
import bsdd_gui

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


def connect_main_window(
    main_window: Type[tool.MainWindowWidget], class_tree: Type[tool.ClassTreeView]
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
    else:
        action.setText(QCoreApplication.translate("MainWindow", "Show Console"))


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
    main_window: Type[tool.MainWindowWidget], file_lock: Type[tool.FileLock], event
):
    file_lock.unlock_file()