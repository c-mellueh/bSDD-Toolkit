from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING, Any, Iterable
from PySide6.QtWidgets import (
    QWidget,
    QAbstractItemView,
    QMenu,
    QLineEdit,
    QLabel,
    QComboBox,
    QTextEdit,
    QCheckBox,
)
from PySide6.QtCore import QObject, Signal, QAbstractItemModel
from PySide6.QtGui import QAction
from bsdd_gui.presets.ui_presets.label_tags_input import TagInput

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


class WidgetSignaller(QObject):
    field_changed = Signal(
        QWidget, QWidget
    )  # Widget in which the field is embedded and Fieldwidget itself


class WidgetHandler(ABC):
    signaller = WidgetSignaller()

    @classmethod
    @abstractmethod
    def get_properties(cls) -> WidgetHandlerProperties:
        return None

    @classmethod
    def register_widget(cls, view: QAbstractItemView):
        logging.info(f"Register {view}")

        cls.get_properties().widgets.add(view)
        cls.get_properties().field_getter[view] = dict()
        cls.get_properties().field_setter[view] = dict()

    @classmethod
    def unregister_widget(cls, view: QWidget):
        logging.info(f"Unregister {view}")
        if not view in cls.get_properties().widgets:
            return
        cls.get_properties().widgets.remove(view)
        cls.get_properties().field_getter.pop(view)
        cls.get_properties().field_setter.pop(view)

    @classmethod
    def get_widgets(cls):
        return cls.get_properties().widgets

    @classmethod
    def register_basic_field(cls, widget: QWidget, field: QWidget, variable_name: str):
        cls.register_field_getter(widget, field, lambda e, vn=variable_name: getattr(e, vn))
        cls.register_field_setter(
            widget,
            field,
            lambda e, v, vn=variable_name: setattr(e, vn, v),
        )
        cls.register_field_listener(widget, field)

    @classmethod
    def register_field_getter(cls, widget: QWidget, field: QWidget, getter_func: callable):
        """_summary_

        Args:
            widget (QWidget): _description_
            field (QWidget): _description_
            getter_func (callable): function(element)
        """

        if not widget in cls.get_properties().field_getter:
            cls.get_properties().field_getter[widget] = dict()
        cls.get_properties().field_getter[widget][field] = getter_func

    @classmethod
    def register_field_setter(cls, widget: QWidget, field: QWidget, setter_func: callable):
        if not widget in cls.get_properties().field_setter:
            cls.get_properties().field_setter[widget] = dict()
        cls.get_properties().field_setter[widget][field] = setter_func

    @classmethod
    def register_field_listener(cls, widget: QWidget, field: QWidget):
        f = field
        w = widget
        if isinstance(f, QLineEdit):
            f.editingFinished.connect(lambda: cls.signaller.field_changed.emit(w, f))
        if isinstance(f, QComboBox):
            f.currentTextChanged.connect(lambda: cls.signaller.field_changed.emit(w, f))
        if isinstance(f, QTextEdit):
            f.textChanged.connect(lambda: cls.signaller.field_changed.emit(w, f))
        if isinstance(f, QCheckBox):
            f.checkStateChanged.connect(lambda: cls.signaller.field_changed.emit(w, f))
        if isinstance(f, TagInput):
            f.tagsChanged.connect(lambda: cls.signaller.field_changed.emit(w, f))

    @classmethod
    def add_validator(cls, widget, field, validator_function: callable, result_function: callable):
        """
        Register a validator for a given input field within a widget.

        This method attaches a validator function and a result handler to a UI field.
        Whenever the field's value changes, the validator is executed, and its result is passed
        to the result function for further handling (e.g., marking a QLineEdit red if invalid).

        Args:
            widget (QWidget):
                The parent widget the field belongs to. Used for grouping validators.
            field (QLineEdit | QComboBox | QTextEdit | TagInput):
                The UI element whose value will be validated.
            validator_function (callable):
                A function that takes the field’s current value and the widget as arguments,
                and returns whether the value is valid (e.g., `True`/`False`, or a more detailed result).
            result_function (callable):
                A function that takes the field and the validator result as arguments,
                and applies a reaction (e.g., updating styles, enabling/disabling buttons).

        Example:
            >>> def is_not_empty(value, widget):
            ...     return bool(value.strip())
            >>> def highlight_invalid(field, is_valid):
            ...     field.setStyleSheet("" if is_valid else "background-color: red;")
            >>> MyForm.add_validator(form, line_edit, is_not_empty, highlight_invalid)
        """

        if not widget in cls.get_properties().validator_functions:
            cls.get_properties().validator_functions[widget] = dict()
        cls.get_properties().validator_functions[widget][field] = (
            validator_function,
            result_function,
        )
        rf, vf, f, w = result_function, validator_function, field, widget
        if isinstance(f, QLineEdit):
            f.textChanged.connect(lambda text: rf(f, vf(text, w)))
            rf(f, vf(f.text(), w))
        if isinstance(f, QComboBox):
            f.currentTextChanged.connect(lambda text: rf(f, vf(text, w)))
            rf(f, vf(f.currentText(), w))
        if isinstance(f, QTextEdit):
            f.textChanged.connect(lambda: rf(f, vf(f.toPlainText(), w)))
            rf(f, vf(f.toPlainText(), w))
        if isinstance(f, QCheckBox):
            f.checkStateChanged.connect(lambda state: rf(f, vf(state, w)))
            rf(f, vf(f.text(), w))
        if isinstance(f, TagInput):
            f.tagsChanged.connect(lambda: rf(f, vf(f.tags(), w)))
            rf(f, vf(f.tags(), w))

    @classmethod
    def sync_from_model(cls, widget: QWidget, element):

        for field, getter_func in cls.get_properties().field_getter[widget].items():
            value = getter_func(element)
            if isinstance(field, QLineEdit):
                field.setText(value)
            if isinstance(field, QLabel):
                field.setText(value)
            if isinstance(field, QComboBox):
                field.setCurrentText(value)
            if isinstance(field, QTextEdit):
                field.setPlainText(value)
            if isinstance(field, QCheckBox):
                field.setChecked(value)
            if isinstance(field, TagInput):
                field.setTags(value or [])

    @classmethod
    def sync_to_model(cls, widget: QWidget, element, explicit_field: QWidget = None):
        field_dict = cls.get_properties().field_setter.get(widget) or dict()
        for field, setter_func in field_dict.items():
            if explicit_field is not None and explicit_field != field:
                continue
            if isinstance(field, QLineEdit):
                setter_func(element, field.text())
            if isinstance(field, QComboBox):
                setter_func(element, field.currentIndex())
            if isinstance(field, QTextEdit):
                setter_func(element, field.toPlainText())
            if isinstance(field, QCheckBox):
                setter_func(element, field.isChecked())
            if isinstance(field, TagInput):
                setter_func(element, field.tags())

    @classmethod
    def all_inputs_are_valid(cls, widget: QWidget):
        function_dict = cls.get_properties().validator_functions.get(widget)
        if not function_dict:
            return
        for f, (validator_function, result_function) in function_dict.items():
            if isinstance(f, QLineEdit):
                is_valid = validator_function(f.text(), widget)
            elif isinstance(f, QComboBox):
                is_valid = validator_function(f.currentText(), widget)
            elif isinstance(f, QTextEdit):
                is_valid = validator_function(f.toPlainText(), widget)
            elif isinstance(f, TagInput):
                is_valid = validator_function(f.tags(), widget)
            if not is_valid:
                return False
        return True


class ViewSignaller(QObject):
    model_refresh_requested = Signal()
    selection_changed = Signal(QWidget, Any)
    delete_selection_requested = Signal(QWidget)


class ViewHandler(WidgetHandler):
    @classmethod
    @abstractmethod
    def get_properties(cls) -> ViewHandlerProperties:
        return None

    @classmethod
    @abstractmethod
    def get_selected(cls, view: QWidget) -> list[object]:
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
