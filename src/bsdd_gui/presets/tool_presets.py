from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING, Any, Iterable
from PySide6.QtWidgets import QWidget, QAbstractItemView, QMenu, QMenuBar
from PySide6.QtCore import QObject, Signal, QAbstractItemModel
from PySide6.QtGui import QAction
import logging

if TYPE_CHECKING:
    from .prop_presets import (
        ColumnHandlerProperties,
        ViewHandlerProperties,
        WidgetHandlerProperties,
        ContextMenuDict,
    )


class ColumnHandler(ABC):
    @classmethod
    @abstractmethod
    def get_properties(cls) -> ColumnHandlerProperties:
        return None

    @classmethod
    def add_column_to_table(
        cls, model: QAbstractItemModel, name: str, get_function: Callable, set_function=None
    ) -> None:
        """
        Define Column which should be shown in Table
        :param name: Name of Column
        :param get_function: getter function for cell value. SOMcreator.SOMProperty will be passed as argument
        set_function: function(model,index,new_value)
        :return:
        """
        if not model in cls.get_properties().columns:
            cls.get_properties().columns[model] = list()
        cls.get_properties().columns[model].append((name, get_function, set_function))

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

    @classmethod
    def set_value_functions(cls, model: QAbstractItemModel):
        """_summary_
        model,index,new_value
        Args:
            model (QAbstractItemModel): _description_

        Returns:
            _type_: _description_
        """
        return [x[2] for x in cls.get_properties().columns.get(model) or []]

    @classmethod
    def get_model(cls):
        return cls.get_properties().model


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
        logging.info(f"Unregister {view}")
        if not view in cls.get_properties().widgets:
            return
        cls.get_properties().widgets.remove(view)

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
    @abstractmethod
    def get_properties(cls) -> ViewHandlerProperties:
        return None

    @classmethod
    def reset_view(cls, view: QAbstractItemView):
        source_model = view.model().sourceModel()
        source_model.beginResetModel()
        source_model.endResetModel()

    @classmethod
    def clear_context_menu_list(cls, view: QAbstractItemView):
        prop = cls.get_properties()
        prop.context_menu_list[view] = list()

    @classmethod
    def add_context_menu_entry(
        cls,
        view: QAbstractItemView,
        label_func: Callable,  # clearer than "name_getter"
        action_func: Callable,  # "function" → "action_func"
        require_selection: bool,  # clearer than "on_selection"
        allow_single: bool,  # clearer than "single"
        allow_multi: bool,  # clearer than "multi"
    ) -> ContextMenuDict:
        """
        Adds an entry to the context menu.

        :param label_func: Callable that returns the display label for the menu entry.
        :param action_func: Callable executed when the menu entry is triggered.
        :param require_selection: Entry only available if at least one item is selected.
        :param allow_single: Entry is available for single selection.
        :param allow_multi: Entry is available for multi-selection.
        :return: A dictionary representing the context menu entry.
        """

        entry: ContextMenuDict = dict()
        entry["label_func"] = label_func
        entry["action_func"] = action_func
        entry["allow_multi"] = allow_multi
        entry["allow_single"] = allow_single
        entry["require_selection"] = require_selection

        props = cls.get_properties()
        props.context_menu_list[view].append(entry)
        return entry

    @classmethod
    def create_context_menu(cls, view: QAbstractItemView, selected_elements: list) -> QMenu:
        menu = QMenu(parent=view)
        props = cls.get_properties()

        entries: Iterable[ContextMenuDict] = props.context_menu_list.get(view, [])
        sel_count = len(selected_elements)

        def eligible(e: ContextMenuDict) -> bool:
            # require_selection → block when nothing selected
            if e["require_selection"] and sel_count == 0:
                return False
            # if nothing selected and not required, allow
            if sel_count == 0:
                return True
            # single vs multi
            if sel_count == 1:
                return e["allow_single"]
            return e["allow_multi"]

        # Materialize the filtered list (not a lazy filter iterator)
        visible_entries = [e for e in entries if eligible(e)]

        for e in visible_entries:
            # Always refresh the label (could depend on current selection/state)
            text = e["label_func"]()
            action = menu.addAction(text)
            # Do not keep old connections around; create a fresh action per menu build
            action.triggered.connect(e["action_func"])
            # If you still want to store the last-built QAction:
            e["action"] = action

        return menu
