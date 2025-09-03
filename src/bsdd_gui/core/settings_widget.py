from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Type

from PySide6.QtCore import QCoreApplication

from bsdd_gui import tool

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_menu_actions(
    settings: Type[tool.SettingsWidget], main_window: Type[tool.MainWindowWidget]
) -> None:
    from bsdd_gui.module.settings_widget import trigger

    action = main_window.add_action("menuData", "Settings", trigger.open_window)
    settings.set_action("open_window", action)


def retranslate_ui(settings: Type[tool.SettingsWidget], util: Type[tool.Util]):
    open_window_action = settings.get_action("open_window")
    title = QCoreApplication.translate("Settings", "Settings")

    open_window_action.setText(title)
    widget = settings.get_widget()
    if widget:
        widget.ui.retranslateUi(widget)
        widget.setWindowTitle(util.get_window_title(title))


def open_window(settings: Type[tool.SettingsWidget]):
    logging.info(f"Opening Settings Window")
    dialog = settings.create_dialog()
    from bsdd_gui.module.settings_widget import trigger

    trigger.retranslate_ui()
    if dialog.exec():
        for func in settings.get_accept_functions():
            func()
    settings.close()
