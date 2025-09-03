from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget

from PySide6.QtCore import QObject, Signal
from .view_presets import ItemViewType


class FieldSignals(QObject):
    field_changed = Signal(
        ItemViewType, ItemViewType
    )  # Widget in which the field is embedded and Fieldwidget itself


class WidgetSignals(FieldSignals):
    widget_requested = Signal(object, ItemViewType)  # data, parent
    widget_created = Signal(ItemViewType)
    widget_closed = Signal(ItemViewType)


class ViewSignals(QObject):
    model_refresh_requested = Signal()
    selection_changed = Signal(ItemViewType, Any)
    delete_selection_requested = Signal(Any)  # ItemViewType
    item_deleted = Signal(object)  # Write BsddClass, BsddProperty etc not QModelIndex in Signal
