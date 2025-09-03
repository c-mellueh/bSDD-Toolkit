from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QPushButton

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_signals(console: Type[tool.ConsoleWidget]):
    console.connect_internal_signals()


def connect_to_main_window(
    main_menu: Type[tool.MainWindowWidget], console: Type[tool.ConsoleWidget]
):
    status_bar = main_menu.get_statusbar()
    button = QPushButton(QCoreApplication.translate("terminal", "Shell"))
    button.setMaximumWidth(60)
    status_bar.addPermanentWidget(button)
    button.clicked.connect(lambda *_: console.request_widget())


def retranslate_ui(console: Type[tool.ConsoleWidget]):
    return


def create_widget(console: Type[tool.ConsoleWidget]):
    console.create_widget()


def close_widget(console: Type[tool.ConsoleWidget]):
    console.unregister_widget(console)
