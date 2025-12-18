from __future__ import annotations
from typing import TYPE_CHECKING
import ctypes
import sys

from PySide6.QtWidgets import QApplication, QMenu, QMenuBar, QStatusBar, QLabel
import bsdd_gui
from bsdd_gui.module.main_window_widget import ui
from bsdd_json.models import BsddClass, BsddClassProperty
from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel
from PySide6.QtGui import QAction
from bsdd_gui.module.main_window_widget import trigger
from bsdd_gui.presets.tool_presets import ActionTool

if TYPE_CHECKING:
    from bsdd_gui.module.main_window_widget.prop import MainWindowWidgetProperties


class Signals(QObject):
    active_class_changed = Signal(BsddClass)
    active_pset_changed = Signal(str)
    active_property_changed = Signal(BsddClassProperty)
    new_class_requested = Signal()
    copy_active_class_requested = Signal()
    new_property_set_requested = Signal()
    new_property_requested = Signal()
    refresh_status_bar_requested = Signal()
    toggle_console_requested = Signal()


class MainWindowWidget(ActionTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> MainWindowWidgetProperties:
        return bsdd_gui.MainWindowWidgetProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.refresh_status_bar_requested.connect(trigger.refresh_status_bar)
        cls.signals.toggle_console_requested.connect(trigger.toggle_console)

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
            cls.get_properties().status_text_label = QLabel()
            cls.get_statusbar().addPermanentWidget(cls.get_properties().status_text_label)
            cls.get_statusbar().setSizeGripEnabled(False)
        return cls.get_properties().ui

    @classmethod
    def get(cls) -> ui.MainWindow:
        return cls.get_properties().ui

    @classmethod
    def get_app(cls) -> QApplication:
        return cls.get_properties().application

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
    def add_action(
        cls,
        parent_name: str,
        name: str,
        function: callable,
        icon=None,
        shortcut=None,
        shortcut_context=None,
    ) -> QAction:
        if parent_name:
            menu: QMenuBar | QMenu = getattr(cls.get(), parent_name)
        else:
            menu = cls.get_menu_bar()
        action = menu.addAction(name)
        action.triggered.connect(function)
        if icon:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(shortcut)
        if shortcut_context:
            action.setShortcutContext(shortcut_context)
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

    @classmethod
    def set_status_bar_text(cls, text: str):
        cls.get_properties().status_text_label.setText(text)

    @classmethod
    def toggle_console(cls):
        active_window = cls.get_app().activeWindow()
        # Cross-platform toggle: on Windows, show/hide OS console window;
        # on non-Windows, open/close the embedded ShellWidget.
        if cls.is_console_visible():
            cls.hide_console()
        else:
            cls.show_console()
        active_window.activateWindow()

    @classmethod
    def hide_console(cls):
        """
        Hide console.
        - Windows: hide the OS console window.
        - Other OS: close the embedded ShellWidget if open.
        :return:
        """
        if sys.platform.startswith("win"):
            hWnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hWnd != 0:
                ctypes.windll.user32.ShowWindow(hWnd, 0)
        else:
            # Ignore if not on Windows
            pass

    @classmethod
    def show_console(cls):
        if sys.platform.startswith("win"):
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            if console_window != 0:
                ctypes.windll.user32.ShowWindow(console_window, 5)  # Show the console
        else:
            # Ignore if not on Windows
            pass

    @classmethod
    def is_console_visible(cls):
        if sys.platform.startswith("win"):
            hWnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hWnd == 0:
                return False
            return bool(ctypes.windll.user32.IsWindowVisible(hWnd))
        else:
            # Ignore if not on Windows
            return False
