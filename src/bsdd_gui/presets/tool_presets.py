from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING, Any
from PySide6.QtWidgets import QWidget, QAbstractItemView
from PySide6.QtCore import QObject, Signal, QAbstractItemModel

if TYPE_CHECKING:
    from .prop_presets import ColumnHandlerProperties, ViewHandlerProperties


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


class WidgetHandler(ABC):

    @classmethod
    @abstractmethod
    def get_properties(cls) -> ViewHandlerProperties:
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
    model_refresh_requested = Signal()
    selection_changed = Signal(QWidget, Any)


class ViewHandler(WidgetHandler):

    @classmethod
    def reset_view(cls, view: QAbstractItemView):
        source_model = view.model().sourceModel()
        source_model.beginResetModel()
        source_model.endResetModel()
