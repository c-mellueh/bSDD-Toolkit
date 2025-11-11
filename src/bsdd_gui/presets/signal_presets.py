from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QAbstractItemView

from PySide6.QtCore import QObject, Signal
from bsdd_gui.presets.ui_presets import FieldWidget, BaseDialog


class WidgetSignals(QObject):
    widget_requested = Signal()
    widget_closed = Signal(FieldWidget)


class FieldSignals(WidgetSignals):
    field_changed = Signal(
        FieldWidget, QWidget
    )  # Widget in which the field is embedded and Fieldwidget itself
    widget_requested = Signal(object, FieldWidget)  # data, parent


class DialogSignals(FieldSignals):
    dialog_accepted = Signal(BaseDialog)
    dialog_declined = Signal(BaseDialog)
    dialog_requested = Signal(Any,QWidget) #Data, Parent

class ViewSignals(QObject):
    model_refresh_requested = Signal()
    selection_changed = Signal(
        QAbstractItemView, Any
    )  # View in which the selection changed, new selection
    delete_selection_requested = Signal(Any)  # ItemViewType
    item_removed = Signal(object)  # Write BsddClass, BsddProperty etc not QModelIndex in Signal
    item_added = Signal(object)  # Write BsddClass, BsddProperty etc not QModelIndex in Signal