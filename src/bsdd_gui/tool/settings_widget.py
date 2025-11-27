from __future__ import annotations

from typing import Callable, TYPE_CHECKING, Type

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTabWidget, QToolBox, QWidget

import bsdd_gui
from bsdd_gui.module.settings_widget import ui

if TYPE_CHECKING:
    from bsdd_gui.module.settings_widget.prop import SettingsWidgetProperties


class SettingsWidget:
    @classmethod
    def get_properties(cls) -> SettingsWidgetProperties:
        return bsdd_gui.SettingsWidgetProperties

    @classmethod
    def set_action(cls, name: str, action: QAction):
        cls.get_properties().actions[name] = action

    @classmethod
    def get_action(cls, name):
        return cls.get_properties().actions[name]

    @classmethod
    def close(cls):
        pass

    @classmethod
    def add_page_to_toolbox(cls, widget_function, page_name: str, accept_function: Callable):
        if page_name not in cls.get_page_dict():
            cls.get_properties().page_dict[page_name] = list()
        cls.get_properties().page_dict[page_name].append(widget_function)
        cls.get_properties().accept_functions.append(accept_function)

    @classmethod
    def get_widget(cls) -> ui.Dialog:
        return cls.get_properties().widget

    @classmethod
    def set_widget(cls, widget: ui.Dialog):
        cls.get_properties().widget = widget

    @classmethod
    def create_dialog(cls) -> ui.Dialog:
        settings_dialog = ui.Dialog()
        cls.set_widget(settings_dialog)
        for name, widgets in cls.get_page_dict().items():
            page = getattr(cls.get_widget().ui, name)
            for widget in widgets:
                page.layout().addWidget(widget())
        settings_dialog.resize(QSize(800, 500))
        return settings_dialog

    @classmethod
    def get_page_dict(cls) -> dict[str, list[Type[QWidget]]]:
        return cls.get_properties().page_dict

    @classmethod
    def create_tab(cls, tab_widget: QTabWidget, tab_name: str) -> QToolBox:
        tb = QToolBox()
        tab_widget.addTab(tb, tab_name)
        return tb

    @classmethod
    def get_accept_functions(cls) -> list[Callable]:
        return cls.get_properties().accept_functions
