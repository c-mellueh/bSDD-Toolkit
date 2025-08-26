from __future__ import annotations
from PySide6.QtWidgets import QApplication
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_window(
    application: QApplication,
    main_window: Type[tool.MainWindow],
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


def connect_main_window(main_window: Type[tool.MainWindow], pset_list: Type[tool.PropertySetTable]):
    main_window.signaller.active_class_changed.connect(
        lambda c: main_window.set_class_text(c.Name if c is not None else "")
    )
    main_window.signaller.active_pset_changed.connect(main_window.set_pset_text)
    main_window.signaller.active_property_changed.connect(
        lambda p: main_window.set_property_text(p.Code)
    )
    signaller = main_window.signaller
    ui = main_window.get()
    ui.button_classes_add.clicked.connect(signaller.new_class_requested.emit)
    ui.button_Pset_add.clicked.connect(signaller.new_property_set_requested.emit)
    ui.button_property_add.clicked.connect(signaller.new_property_requested.emit)
