from PySide6.QtWidgets import QApplication
from bsdd_gui import tool
from typing import Type

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