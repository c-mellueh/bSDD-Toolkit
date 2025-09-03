from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QPushButton

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_signals(shell: Type[tool.ShellWidget]):
    shell.connect_internal_signals()


def connect_to_main_window(main_menu: Type[tool.MainWindowWidget], shell: Type[tool.ShellWidget]):
    status_bar = main_menu.get_statusbar()
    button = QPushButton(QCoreApplication.translate("terminal", "Shell"))
    button.setMaximumWidth(60)
    status_bar.addPermanentWidget(button)
    button.clicked.connect(lambda *_: shell.request_widget())


def retranslate_ui(shell: Type[tool.ShellWidget]):
    return


def create_widget(shell: Type[tool.ShellWidget]):
    shell.create_widget()


def close_widget(shell: Type[tool.ShellWidget]):
    shell.unregister_widget(shell)
