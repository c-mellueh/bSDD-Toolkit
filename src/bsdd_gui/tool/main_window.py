from __future__ import annotations
from typing import TYPE_CHECKING
import ctypes

from PySide6.QtWidgets import QApplication
import bsdd_gui
from bsdd_gui.module.main_window import ui

if TYPE_CHECKING:
    from bsdd_gui.module.main_window.prop import MainWindowProperties

class MainWindow:
    @classmethod
    def get_properties(cls) -> MainWindowProperties:
        return bsdd_gui.MainWindowProperties
    
    @classmethod
    def create(cls, application: QApplication) -> ui.MainWindow:
        """
        Create UI and save the Application to properties
        :param application:
        :return:
        """
        if cls.get_properties().window is None:
            window = ui.MainWindow(application)
            cls.get_properties().window = window
            cls.get_properties().ui = window.ui
            cls.get_properties().application = application
        return cls.get_properties().window
    
    @classmethod
    def hide_console(cls):
        """
        hide Console Window (Works only for Windows so far)
        :return:
        """
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd != 0:
            ctypes.windll.user32.ShowWindow(hWnd, 0)