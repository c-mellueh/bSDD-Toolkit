from __future__ import annotations
from typing import TYPE_CHECKING
import ctypes

from PySide6.QtWidgets import QApplication
import bsdd_gui
from bsdd_gui.module.main_window import ui
from bsdd_parser.models import BsddClass,BsddClassProperty
from PySide6.QtCore import QObject, Signal,QSortFilterProxyModel

if TYPE_CHECKING:
    from bsdd_gui.module.main_window.prop import MainWindowProperties

class Signaller(QObject):
    active_class_changed = Signal(BsddClass)
    active_pset_changed = Signal(str)
    active_property_changed = Signal(BsddClassProperty)


class MainWindow:
    signaller = Signaller()
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
        return
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd != 0:
            ctypes.windll.user32.ShowWindow(hWnd, 0)
        
    @classmethod
    def get_active_class(cls) -> BsddClass|None:
        return cls.get_properties().active_class

    @classmethod
    def set_active_class(cls,value:BsddClass):
        cls.get_properties().active_class = value
        cls.signaller.active_class_changed.emit(cls.get_properties().active_class)
    
    @classmethod
    def set_active_pset(cls,value:str):
        cls.get_properties().active_pset = value
        cls.signaller.active_pset_changed.emit(value)
    
    @classmethod
    def set_active_property(cls,value:BsddClassProperty):
        cls.get_properties().active_property = value
        cls.signaller.active_property_changed.emit(value)
    
    
    @classmethod
    def get_class_view(cls):
        return cls.get_properties().ui.tree_class
    
    @classmethod
    def get_pset_view(cls):
        return cls.get_properties().ui.table_pset
    
    @classmethod
    def get_property_view(cls):
        return cls.get_properties().ui.table_property