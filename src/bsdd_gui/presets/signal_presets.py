from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QAbstractItemView

from PySide6.QtCore import QObject, Signal
from bsdd_gui.presets.ui_presets import FieldWidget, BaseDialog, BaseWindow

import logging


class BaseSignal(QObject):

    def get_signals(self) -> dict[str, Signal]:
        return {name: obj for name, obj in self.__dict__.items() if isinstance(obj, Signal)}

    def dk(self):
        s_dict = self.get_signals()
        for signal in s_dict.keys():
            try:
                getattr(self, signal).disconnect()
            except Exception as e:
                logging.debug(str(e))



class WidgetSignals(BaseSignal):
    widget_requested = Signal()
    widget_closed = Signal(BaseWindow)
    widget_created = Signal(BaseWindow)
    widget_shown = Signal(BaseWindow)
    widget_hidden = Signal(BaseWindow)
    widget_resized = Signal(BaseWindow)
    widget_entered = Signal(BaseWindow)


class FieldSignals(WidgetSignals):
    field_changed = Signal(
        FieldWidget, QWidget
    )  # Widget in which the field is embedded and Fieldwidget itself
    widget_requested = Signal(object, FieldWidget)  # data, parent


class DialogSignals(FieldSignals):
    dialog_accepted = Signal(BaseDialog)
    dialog_declined = Signal(BaseDialog)
    dialog_requested = Signal(Any, QWidget)  # Data, Parent


class ViewSignals(BaseSignal):
    model_refresh_requested = Signal()
    selection_changed = Signal(
        QAbstractItemView, Any
    )  # View in which the selection changed, new selection
    delete_selection_requested = Signal(Any)  # ItemViewType
    item_removed = Signal(object)  # Write BsddClass, BsddProperty etc not QModelIndex in Signal
    item_added = Signal(object)  # Write BsddClass, BsddProperty etc not QModelIndex in Signal
