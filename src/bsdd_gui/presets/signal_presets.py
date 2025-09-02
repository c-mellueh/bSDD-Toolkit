from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget

from PySide6.QtCore import QObject, Signal
from .view_presets import ItemViewType


class FieldSignals(QObject):
    field_changed = Signal(
        QWidget, QWidget
    )  # Widget in which the field is embedded and Fieldwidget itself


class WidgetSignals(FieldSignals):
    widget_requested = Signal(object, QWidget)  # data, parent
    widget_created = Signal(QWidget)
    widget_closed = Signal(QWidget)


class ViewSignals(WidgetSignals):
    view_closed = Signal(object)
    model_refresh_requested = Signal()
    selection_changed = Signal(QWidget, Any)
    delete_selection_requested = Signal(Any)  # ItemViewType
    item_deleted = Signal(object)  # Write BsddClass, BsddProperty etc not QModelIndex in Signal
