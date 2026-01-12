from __future__ import annotations

from typing import TYPE_CHECKING, Type

from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    from bsdd_gui import tool
from bsdd_gui.module.logging import ui
import os
import logging
from bsdd_gui.module.logging import constants


def add_settings_page(func,settings:Type[tool.SettingsWidget]):
    settings.add_page_to_toolbox(ui.SettingsWidget,"pageLogging",func)

def create_logger(
    logging_tool: Type[tool.Logging],
    util: Type[tool.Util],
    main_window: Type[tool.MainWindowWidget],
):
    log_dir_path = logging_tool.get_logging_directory()
    if not os.path.exists(log_dir_path):
        util.create_directory(log_dir_path)

    logger = logging_tool.get_logger()
    logger.setLevel(logging_tool.get_log_level())

    logging_tool.get_signals()  # create signals
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(logging_tool.create_console_handler())
    logger.addHandler(logging_tool.create_file_handler(logging_tool.get_logging_filename()))
    logger.addHandler(
        logging_tool.create_popup_handler(main_window.get())
    )  # creates Popup if Error/Warning is logged
    logging_tool.create_error_popup()  # creates Popup if error is raised


def retranslate_ui(logging_tool: Type[tool.Logging]):
    widget = logging_tool.get_settings_widget()
    if not widget:
        return
    widget.ui.widget_export.name = QCoreApplication.translate("Logging", "Log Directory:")
    widget.ui.retranslateUi(widget)


def settings_accepted(logging_tool: Type[tool.Logging], util: Type[tool.Util]):
    log_levels: dict[str, int] = logging._nameToLevel
    widget = logging_tool.get_settings_widget()
    level = log_levels[widget.ui.comboBox.currentText().upper()]
    logging_tool.set_log_level(level)

    path = util.get_path_from_fileselector(widget.ui.widget_export)[0]
    logging_tool.set_logging_directory(path)


def settings_widget_created(
    widget: ui.SettingsWidget, logging_tool: Type[tool.Logging], util: Type[tool.Util]
):
    logging_tool.set_settings_widget(widget)
    names = [l[0].title() for l in sorted(logging._nameToLevel.items(), key=lambda x: x[1])]
    cb = widget.ui.comboBox
    cb.clear()
    cb.addItems(names)
    current_log_name = logging._levelToName[logging_tool.get_log_level()]
    cb.setCurrentText(current_log_name.title())
    util.fill_file_selector(
        widget.ui.widget_export,
        "",
        None,
        constants.LOG_PATH,
        request_folder=True,
        request_save=True,
        update_appdata=False,
    )
    retranslate_ui(logging_tool)
