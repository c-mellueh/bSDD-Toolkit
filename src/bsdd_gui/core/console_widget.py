from __future__ import annotations

from typing import TYPE_CHECKING, Type

from PySide6.QtWidgets import QPushButton

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_signals(console: Type[tool.ConsoleWidget]):
    console.connect_internal_signals()


def connect_to_main_window(
    main_menu: Type[tool.MainWindowWidget], console: Type[tool.ConsoleWidget]
):
    status_bar = main_menu.get_statusbar()
    button = QPushButton("C")
    button.setMaximumWidth(24)
    status_bar.addPermanentWidget(button)
    button.clicked.connect(lambda *_: console.signals.widget_requested.emit())


def retranslate_ui(console: Type[tool.ConsoleWidget]):
    return


def close_widget(console: Type[tool.ConsoleWidget]):
    console.unregister_widget(console)
