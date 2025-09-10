from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QPushButton

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.shell_widget import ui


def connect_signals(shell: Type[tool.ShellWidget]):
    shell.connect_internal_signals()


def connect_to_main_window(main_menu: Type[tool.MainWindowWidget], shell: Type[tool.ShellWidget]):
    toggle_console_action = main_menu.add_action("menuEdit", "Show Shell", shell.request_widget)
    shell.set_action(main_menu.get(), "toggle_console", toggle_console_action)


def retranslate_ui(shell: Type[tool.ShellWidget], main_window: Type[tool.MainWindowWidget]):
    shell.get_action(main_window.get(), "toggle_console").setText(
        QCoreApplication.translate("Shell", "Show Shell")
    )


def create_widget(shell: Type[tool.ShellWidget]):
    widget: ui.PythonConsole = shell.create_widget()
    widget.show()
    widget.raise_()
    widget.activateWindow()


def close_widget(shell: Type[tool.ShellWidget]):
    shell.unregister_widget(shell)
