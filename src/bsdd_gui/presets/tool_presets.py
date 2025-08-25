from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING, Any
from PySide6.QtWidgets import QWidget, QAbstractItemView, QMenu, QMenuBar
from PySide6.QtCore import QObject, Signal, QAbstractItemModel
from PySide6.QtGui import QAction

if TYPE_CHECKING:
    from .prop_presets import (
        ColumnHandlerProperties,
        ViewHandlerProperties,
        WidgetHandlerProperties,
    )


class ColumnHandler(ABC):
    @classmethod
    @abstractmethod
    def get_properties(cls) -> ColumnHandlerProperties:
        return None

    @classmethod
    def add_column_to_table(
        cls, model: QAbstractItemModel, name: str, get_function: Callable
    ) -> None:
        """
        Define Column which should be shown in Table
        :param name: Name of Column
        :param get_function: getter function for cell value. SOMcreator.SOMProperty will be passed as argument
        :return:
        """
        if not model in cls.get_properties().columns:
            cls.get_properties().columns[model] = list()
        cls.get_properties().columns[model].append((name, get_function))

    @classmethod
    def get_column_count(cls, model: QAbstractItemModel):
        columns = cls.get_properties().columns.get(model)
        return len(columns) if columns else 0

    @classmethod
    def get_column_names(cls, model: QAbstractItemModel):
        return [x[0] for x in cls.get_properties().columns.get(model) or []]

    @classmethod
    def get_value_functions(cls, model: QAbstractItemModel):
        return [x[1] for x in cls.get_properties().columns.get(model) or []]


class WidgetSignaller(QObject):
    pass


class ModuleHandler(ABC):
    @classmethod
    @abstractmethod
    def get_properties(cls) -> WidgetHandlerProperties:
        return None

    @classmethod
    def set_action(cls, widget, name: str, action: QAction):
        """
        save all actions so that the translation functions work
        """
        if not widget in cls.get_properties().actions:
            cls.get_properties().actions[widget] = dict()
        cls.get_properties().actions[widget][name] = action

    @classmethod
    def get_action(cls, widget, name):
        return cls.get_properties().actions[widget][name]


class WidgetHandler(ABC):

    @classmethod
    @abstractmethod
    def get_properties(cls) -> WidgetHandlerProperties:
        return None

    @classmethod
    def register_widget(cls, view: QAbstractItemView):
        cls.get_properties().widgets.add(view)

    @classmethod
    def unregister_widget(cls, view: QWidget):
        cls.get_properties().widgets.pop(view)

    @classmethod
    def get_widgets(cls):
        return cls.get_properties().widgets


class ViewSignaller(QObject):

    @classmethod
    @abstractmethod
    def get_properties(cls) -> ViewHandlerProperties:
        return None

    model_refresh_requested = Signal()
    selection_changed = Signal(QWidget, Any)


class ViewHandler(WidgetHandler):

    @classmethod
    def reset_view(cls, view: QAbstractItemView):
        source_model = view.model().sourceModel()
        source_model.beginResetModel()
        source_model.endResetModel()
