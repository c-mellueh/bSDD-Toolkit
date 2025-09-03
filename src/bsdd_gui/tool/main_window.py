from __future__ import annotations
from typing import TYPE_CHECKING
import ctypes

from PySide6.QtWidgets import QApplication, QMenu, QMenuBar, QStatusBar
import bsdd_gui
from bsdd_gui.module.main_window import ui
from bsdd_parser.models import BsddClass, BsddClassProperty
from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel
from PySide6.QtGui import QAction
from bsdd_gui.module.main_window import trigger

if TYPE_CHECKING:
    from bsdd_gui.module.main_window.prop import MainWindowProperties


class Signals(QObject):
    active_class_changed = Signal(BsddClass)
    active_pset_changed = Signal(str)
    active_property_changed = Signal(BsddClassProperty)
    new_class_requested = Signal()
    copy_active_class_requested = Signal()
    new_property_set_requested = Signal()
    new_property_requested = Signal()


class MainWindow:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> MainWindowProperties:
        return bsdd_gui.MainWindowProperties

    @classmethod
    def connect_internal_signals(cls):
        pass

    @classmethod
    def create(cls, application: QApplication) -> ui.MainWindow:
        """
        Create UI and save the Application to properties
        :param application:
        :return:
        """
        if cls.get_properties().window is None:
            window = ui.MainWindow(application)
            cls.get_properties().ui = window
            cls.get_properties().application = application
        return cls.get_properties().ui

    @classmethod
    def get(cls) -> ui.MainWindow:
        return cls.get_properties().ui

    @classmethod
    def get_app(cls) -> QApplication:
        return cls.get_properties().application

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
    def get_active_class(cls) -> BsddClass | None:
        return cls.get_properties().active_class

    @classmethod
    def get_active_pset(cls) -> str:
        return cls.get_properties().active_pset

    @classmethod
    def get_active_property(cls):
        return cls.get_properties().active_property

    @classmethod
    def set_active_class(cls, value: BsddClass):
        cls.get_properties().active_class = value
        cls.signals.active_class_changed.emit(cls.get_properties().active_class)

    @classmethod
    def set_active_pset(cls, value: str):
        cls.get_properties().active_pset = value
        cls.signals.active_pset_changed.emit(value)

    @classmethod
    def set_active_property(cls, value: BsddClassProperty):
        cls.get_properties().active_property = value
        cls.signals.active_property_changed.emit(value)

    @classmethod
    @classmethod
    def get_class_view(cls):
        return cls.get().tree_class

    @classmethod
    def get_pset_view(cls):
        return cls.get().table_pset

    @classmethod
    def get_property_view(cls):
        return cls.get().table_property

    @classmethod
    def set_class_text(cls, text: str):
        cls.get().label_class_name.setText(text)

    @classmethod
    def set_pset_text(cls, text: str):
        cls.get().label_pset_name.setText(text)

    @classmethod
    def set_property_text(cls, text: str):
        cls.get().label_property_name.setText(text)

    @classmethod
    def add_action(cls, parent_name: str, name: str, function: callable) -> QAction:
        if parent_name:
            menu: QMenuBar | QMenu = getattr(cls.get(), parent_name)
        else:
            menu = cls.get_menu_bar()
        action = menu.addAction(name)
        action.triggered.connect(function)
        return action

    @classmethod
    def remove_action(cls, parent_name: str, action: QAction):
        if parent_name:
            menu: QMenuBar | QMenu = getattr(cls.get(), parent_name)
        else:
            menu = cls.get_menu_bar()
        menu.removeAction(action)

    @classmethod
    def get_menu_bar(cls) -> QMenuBar:
        return cls.get().menubar

    @classmethod
    def add_submenu(cls, parent_name: str, name) -> QMenu:
        if parent_name:
            menu: QMenuBar | QMenu = getattr(cls.get(), parent_name)
        else:
            menu = cls.get_menu_bar()
        return menu.addMenu(name)

    @classmethod
    def remove_submenu(cls, parent_name: str, sub_menu: QMenu):
        if parent_name:
            menu: QMenuBar | QMenu = getattr(cls.get(), parent_name)
        else:
            menu = cls.get_menu_bar()
        menu.removeAction(sub_menu.menuAction())

    @classmethod
    def install_validation_styles(cls, app: QApplication) -> None:
        app.setStyleSheet(
            app.styleSheet()
            + """
            QLineEdit[invalid="true"],
            QComboBox[invalid="true"] {
                border: 1px solid red;
                border-radius: 4px;
            }
            /* checkbox: highlight the indicator when invalid */
            QCheckBox[invalid="true"]::indicator {
                border: 1px solid red;
            }
        """
        )

    @classmethod
    def get_statusbar(cls) -> QStatusBar:
        return cls.get().statusbar
