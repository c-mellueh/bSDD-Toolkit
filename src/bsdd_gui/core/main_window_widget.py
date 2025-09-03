from __future__ import annotations
from PySide6.QtWidgets import QApplication
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_window(
    application: QApplication,
    main_window: Type[tool.MainWindowWidget],
):
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
