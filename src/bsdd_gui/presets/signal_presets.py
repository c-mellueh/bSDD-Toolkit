from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QAbstractItemView

from PySide6.QtCore import QObject, Signal
from bsdd_gui.presets.ui_presets import BaseWidget, BaseDialog


class WidgetSignals(QObject):
    widget_requested = Signal(object, BaseWidget)  # data, parent
    widget_closed = Signal(BaseWidget)


class FieldSignals(WidgetSignals):
    field_changed = Signal(
        BaseWidget, QWidget
    )  # Widget in which the field is embedded and Fieldwidget itself


class DialogSignals(FieldSignals):
    dialog_accepted = Signal(BaseDialog)
    dialog_declined = Signal(BaseDialog)


class ViewSignals(QObject):
    model_refresh_requested = Signal()
    selection_changed = Signal(
        QAbstractItemView, Any
    )  # View in which the selection changed, new selection
    delete_selection_requested = Signal(Any)  # ItemViewType
    item_deleted = Signal(object)  # Write BsddClass, BsddProperty etc not QModelIndex in Signal
