"""
Tool preset base classes for bsdd_gui.

These presets standardize how tools create widgets, manage actions, wire
signals, and synchronize data between the UI and the underlying model.

At a glance
- ActionTool: Centralizes QAction creation and lookup per widget. Useful for
  menu bars and toolbars, and for translation/retitling of actions.
- WidgetTool: Base for tools that create and manage widgets. Provides
  registration, lifetime, and plugin injection for created widgets.
- FieldTool: Extends WidgetTool for widgets that expose editable fields.
  Adds bidirectional data sync (model ↔ UI), field registration, and
  validation helpers for live editing.
- DialogTool: Extends FieldTool for non-live editing via modal dialogs.
  Hosts a field widget inside a dialog and applies changes on accept.

Notes
- Each concrete tool subclass must implement get_properties() to return its
  corresponding Properties object (e.g. ActionsProperties, WidgetProperties,
  FieldProperties, DialogProperties) used to hold runtime state.
- Tools expose Signals (see signal_presets) that are connected in
  connect_internal_signals(). Subclasses should call super() when overriding.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING, Any, Iterable, Type, TypeAlias
from types import ModuleType
from PySide6.QtWidgets import (
    QWidget,
    QAbstractItemView,
    QMenu,
    QLineEdit,
    QLabel,
    QComboBox,
    QTextEdit,
    QCheckBox,
    QAbstractButton,
    QTreeView,
    QLayout,
    QDateTimeEdit,
)
from PySide6.QtCore import (
    QObject,
    Signal,
    QDateTime,
    Qt,
    QSortFilterProxyModel,
    QModelIndex,
    QItemSelectionModel,
)
from PySide6.QtGui import QAction
from bsdd_gui.presets.ui_presets import (
    TagInput,
    DateTimeWithNow,
    FieldWidget,
    TreeItemView,
    BaseDialog,
    ItemViewType,
    ItemWithToggleSwitch,
)
from bsdd_json import *
import logging
from .signal_presets import WidgetSignals, DialogSignals, ViewSignals, FieldSignals
from .models_presets import ItemModel
import datetime
import re

BsddDataType: TypeAlias = BsddClass | BsddProperty | BsddDictionary | BsddClassProperty

if TYPE_CHECKING:
    from .prop_presets import (
        ActionsProperties,
        ViewProperties,
        WidgetProperties,
        FieldProperties,
        DialogProperties,
        ContextMenuDict,
    )


class BaseTool(ABC):
    """Abstract base for all tool presets.

    Subclasses provide a typed Properties object via get_properties(), and
    connect_internal_signals() to wire their signals to triggers/handlers.
    """

    @classmethod
    @abstractmethod
    def get_properties(cls) -> object:
        return None

    @classmethod
    @abstractmethod
    def connect_internal_signals(cls):
        return None


class ActionTool(BaseTool):
    """Preset to standardize QAction management.

    Purpose
    - Store and retrieve QActions per widget, enabling consistent wiring
      and translation/retitling across the application (e.g., menu bars).

    Implement in subclasses
    - get_properties() -> ActionsProperties with an "actions" dict-like
      attribute: { widget: { action_name: QAction } }.

    Usage
    - Call set_action(widget, name, action) after creating an action so it
      can be translated and later retrieved via get_action().
    - Use connect_internal_signals() to hook up action-related signals if
      needed and call super() in overrides.
    """

    @classmethod
    @abstractmethod
    def get_properties(cls) -> ActionsProperties:
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
    def get_action(cls, widget, name) -> QAction:
        widget_data = cls.get_properties().actions.get(widget)
        if not widget_data:
            return None
        return widget_data.get(name)


class WidgetTool(BaseTool):
    """Preset for creating and managing widgets.

    Purpose
    - Provide a standard way to construct widgets, register/unregister them,
      wire core signals, and inject optional plugin widgets into layouts.

    Implement in subclasses
    - get_properties() -> WidgetProperties with:
      * widgets: set[FieldWidget]
      * plugin_widget_list: iterable of plugin descriptors
    - _get_trigger() -> module with functions used by signals (e.g.,
      create_widget()).
    - _get_widget_class() -> Type[FieldWidget] to instantiate in create_widget.

    Key methods
    - create_widget(...): Instantiates, registers, and augments the widget
      with plugin widgets.
    - register_widget/unregister_widget(): Track widget lifetime.
    - request_widget(...): Emit a signal to create a widget via the trigger.
    - add_plugins_to_widget(widget): Insert plugin widgets into a target
      layout on the produced widget.
    """

    signals = WidgetSignals()

    @classmethod
    @abstractmethod
    def get_properties(cls) -> WidgetProperties:
        return None

    @classmethod
    @abstractmethod
    def _get_trigger(cls) -> ModuleType:
        return None

    @classmethod
    @abstractmethod
    def _get_widget_class(cls) -> Type[FieldWidget]:
        logging.error(f"This function needs to be subclassed")
        return None

    @classmethod
    @abstractmethod
    def create_widget(cls, *args, **kwargs) -> FieldWidget:
        widget = cls._get_widget_class()(*args, **kwargs)
        # cls.get_properties().widgets.append(widget) register widget does the same
        cls.add_plugins_to_widget(widget)
        return widget

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.widget_requested.connect(cls._get_trigger().create_widget)
        cls.signals.widget_closed.connect(cls.unregister_widget)

    @classmethod
    def connect_widget_signals(cls, widget: FieldWidget):
        widget.closed.connect(lambda w=widget: cls.signals.widget_closed.emit(w))


    @classmethod
    def register_widget(cls, widget: FieldWidget):
        logging.info(f"Register {widget}")

        cls.get_properties().widgets.append(widget)
        cls.request_retranslate()

    @classmethod
    def unregister_widget(cls, widget: FieldWidget):
        logging.info(f"Unregister {widget}")
        if not widget in cls.get_properties().widgets:
            return False
        cls.get_properties().widgets.remove(widget)
        return True

    @classmethod
    def get_widgets(cls):
        return cls.get_properties().widgets

    @classmethod
    def request_widget(cls, *args, **kwargs):
        """
        connects to trigger.create_widget
        """
        cls.signals.widget_requested.emit(*args, **kwargs)

    @classmethod
    def request_retranslate(cls):
        cls._get_trigger().retranslate_ui()

    @classmethod
    def add_plugins_to_widget(cls, widget):
        for plugin in cls.get_properties().plugin_widget_list:
            layout: QLayout = getattr(widget, plugin.layout_name)
            layout.insertWidget(plugin.index, plugin.widget())
            setattr(cls.get_properties(), plugin.key, plugin.value_getter)


class FieldTool(WidgetTool):
    """Preset for widgets that edit fields with live synchronization.

    Purpose
    - Extend WidgetTool with a consistent pattern to register UI fields,
      read/write values to a model object, listen for changes, and validate
      inputs. Intended for live editing of data.

    Implement in subclasses
    - get_properties() -> FieldProperties with:
      * field_getter/field_setter: dict[widget][field] -> callable
      * validator_functions: dict[widget][field] -> (validator, result_handler)

    Key methods
    - register_basic_field(widget, field, variable_name): Quick mapping of a
      model attribute to a field (getter/setter + listener + initial sync).
    - register_field_getter/register_field_setter(...): Custom value access.
    - register_field_listener(widget, field): Wire change signals per type.
    - sync_from_model(widget, model, explicit_field=None): Model → UI sync.
    - sync_to_model(widget, model, explicit_field=None): UI → Model sync.
    - add_validator(widget, field, validator, result_handler): Per-field
      validation with immediate feedback.
    - all_inputs_are_valid(widget) / get_invalid_inputs(widget): Validation
      utilities for enabling/guarding actions.

    Convenience
    - show_widget(data, parent, ...): Ensure a single visible widget per
      data object; recreate hidden widgets to refresh state.
    - get_widget(data): Look up the existing widget for a given data object.
    """

    signals = FieldSignals()

    @classmethod
    @abstractmethod
    def get_properties(cls) -> FieldProperties:
        return None

    @classmethod
    @abstractmethod
    def create_widget(cls, *args, **kwargs) -> ItemViewType:
        widget = super().create_widget(*args, **kwargs)
        return widget

    @classmethod
    def get_widget(cls, data: object) -> ItemViewType:
        widgets = [widget for widget in cls.get_widgets() if widget.bsdd_data == data]
        if len(widgets) > 1:
            logging.warning(f"Multiple Widgets found for the same data")
        elif not widgets:
            return None
        return widgets[0]

    @classmethod
    def show_widget(cls, data, parent, *args, **kwargs):
        if widget := cls.get_widget(data):
            if widget.isHidden():
                widget.close()
                widget = cls.create_widget(data, parent, *args, **kwargs)
        else:
            widget = cls.create_widget(data, parent, *args, **kwargs)
        widget.show()
        widget.activateWindow()
        widget.showNormal()
        return widget

    @classmethod
    def register_widget(cls, widget: FieldWidget):
        cls.signals.widget_created.emit(widget)
        super().register_widget(widget)
        cls.get_properties().field_getter[widget] = dict()
        cls.get_properties().field_setter[widget] = dict()

    @classmethod
    def unregister_widget(cls, widget: FieldWidget):
        if not super().unregister_widget(widget):
            return
        cls.get_properties().field_getter.pop(widget)
        cls.get_properties().field_setter.pop(widget)

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def register_basic_field(cls, widget: FieldWidget, field: QWidget, variable_name: str):
        cls.register_field_getter(widget, field, lambda e, vn=variable_name: getattr(e, vn))
        cls.register_field_setter(
            widget,
            field,
            lambda e, v, vn=variable_name: setattr(e, vn, v if v is not None else None),
        )
        if hasattr(widget, "bsdd_data"):
            cls.sync_from_model(widget, widget.bsdd_data, explicit_field=field)
        else:
            logging.info(f"Attribute 'bsdd_data' not set for {widget}")
        cls.register_field_listener(widget, field)

    @classmethod
    def register_field_getter(cls, widget: FieldWidget, field: QWidget, getter_func: callable):
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
    def register_field_setter(cls, widget: FieldWidget, field: QWidget, setter_func: callable):
        """
        the setter func gets called with func(data,value)
        """
        if not widget in cls.get_properties().field_setter:
            cls.get_properties().field_setter[widget] = dict()
        cls.get_properties().field_setter[widget][field] = setter_func

    @classmethod
    def register_field_listener(cls, widget: FieldWidget, field: QWidget):
        """
        Listen to changes in the field and emit a signal with the widget and field as arguments.
        """
        w = widget
        r_field = field  # return field -> to wich the model is synced
        c_field = field  # connect field -> to wich the signal is connected

        if isinstance(c_field, ItemWithToggleSwitch):
            c_field.active_toggle.toggled.connect(
                lambda: cls.signals.field_changed.emit(w, r_field)
            )
            c_field = c_field.item
        if isinstance(c_field, QLineEdit):
            c_field.textChanged.connect(lambda: cls.signals.field_changed.emit(w, r_field))
        elif isinstance(c_field, QComboBox):
            c_field.currentTextChanged.connect(lambda: cls.signals.field_changed.emit(w, r_field))
        elif isinstance(c_field, QTextEdit):
            c_field.textChanged.connect(lambda: cls.signals.field_changed.emit(w, r_field))
        elif isinstance(c_field, QCheckBox):
            c_field.checkStateChanged.connect(lambda: cls.signals.field_changed.emit(w, r_field))
        elif isinstance(c_field, TagInput):
            c_field.tagsChanged.connect(lambda: cls.signals.field_changed.emit(w, r_field))
        elif isinstance(c_field, QDateTimeEdit):
            c_field.dateTimeChanged.connect(lambda: cls.signals.field_changed.emit(w, r_field))
        elif isinstance(c_field, QAbstractButton):
            c_field.toggled.connect(lambda: cls.signals.field_changed.emit(w, r_field))

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
        if not field in cls.get_properties().validator_functions[widget]:
            cls.get_properties().validator_functions[widget][field] = list()
        cls.get_properties().validator_functions[widget][field].append(
            (validator_function, result_function)
        )
        rf, vf, f, w = result_function, validator_function, field, widget

        func = lambda: rf(f, vf(cls.get_value_from_field(f), w))

        if isinstance(f, ItemWithToggleSwitch):
            f.active_toggle.toggled.connect(func)
            f = f.item

        if isinstance(f, QLineEdit):
            f.textChanged.connect(func)
        elif isinstance(f, QComboBox):
            f.currentTextChanged.connect(func)
        elif isinstance(f, QTextEdit):
            f.textChanged.connect(func)
        elif isinstance(f, QCheckBox):
            f.checkStateChanged.connect(func)
        elif isinstance(f, TagInput):
            f.tagsChanged.connect(func)
        elif isinstance(f, QDateTimeEdit):
            f.dateTimeChanged.connect(func)
        elif isinstance(f, QAbstractButton):
            f.toggled.connect(func)
        else:
            logging.info("ClassType not Found")
            return
        func()  # initial validation

    @classmethod
    def get_value_from_field(cls, field: QWidget):
        """
        Docstring für get_value_from_field

        :param cls: Beschreibung
        :param field: Beschreibung
        :type field: QWidget
        """
        if isinstance(field, ItemWithToggleSwitch):
            if not field.is_active():
                return None
            field = field.item

        if isinstance(field, QLineEdit):
            value = field.text()
        elif isinstance(field, QComboBox):
            value = field.currentText()
        elif isinstance(field, QTextEdit):
            value = field.toPlainText()
        elif isinstance(field, QCheckBox):
            value = field.isChecked()
        elif isinstance(field, TagInput):
            value = field.tags()
            value = value if value else None
        elif isinstance(field, QDateTimeEdit):
            value = field.dateTime().toPython()
        elif isinstance(field, QAbstractButton):
            value = field.isChecked()
        else:
            value = None
        return value

    @classmethod
    def sync_from_model(cls, widget: FieldWidget, data, explicit_field=None):
        """
        get values from the model and set them to the fields
        """
        if not widget in cls.get_properties().field_getter:
            return
        for field, getter_func in cls.get_properties().field_getter[widget].items():
            if explicit_field is not None and explicit_field != field:
                continue
            value = getter_func(data)
            if isinstance(field, ItemWithToggleSwitch):
                if value is None:
                    field.set_active(False)
                    return
                else:
                    field.set_active(True)
                    field = field.item
            if isinstance(field, QLineEdit):
                field.setText(value)
            elif isinstance(field, QLabel):
                field.setText(value)
            elif isinstance(field, QComboBox):
                field.setCurrentText(value)
            elif isinstance(field, QTextEdit):
                field.setPlainText(value)
            elif isinstance(field, QCheckBox):
                field.setChecked(value or False)
            elif isinstance(field, TagInput):
                field.setTags(value or [])
            elif isinstance(field, QDateTimeEdit):
                if not value:
                    return
                if isinstance(value, str):
                    pattern_with_fraction = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$"
                    fmt = (
                        "%Y-%m-%d %H:%M:%S.%f"
                        if re.match(pattern_with_fraction, value)
                        else "%Y-%m-%d %H:%M:%S"
                    )
                    value = datetime.datetime.strptime(value, fmt)
                field.setDateTime(QDateTime.fromSecsSinceEpoch(int(value.timestamp()), Qt.UTC))
            elif isinstance(field, QAbstractButton):
                field.setChecked(value)

    @classmethod
    def sync_to_model(cls, widget: FieldWidget, element, explicit_field: QWidget = None):
        field_dict = cls.get_properties().field_setter.get(widget) or dict()
        for field, setter_func in field_dict.items():
            if explicit_field is not None and explicit_field != field:
                continue
            value = cls.get_value_from_field(field)
            setter_func(element, value)

    @classmethod
    def all_inputs_are_valid(cls, widget: FieldWidget):
        function_dict = cls.get_properties().validator_functions.get(widget)
        if not function_dict:
            logging.info(f"No Validator Functions found for widget {widget}")
            return True

        for f, validator in function_dict.items():
            for validator_function, result_function in validator:
                value = cls.get_value_from_field(f)
                is_valid = validator_function(value, widget)
                if not is_valid:
                    return False
        return True

    @classmethod
    def get_invalid_inputs(cls, widget: FieldWidget):
        function_dict = cls.get_properties().validator_functions.get(widget)
        if not function_dict:
            return []
        invalid_inputs = list()
        for f, validator in function_dict.items():
            is_valid = True
            for validator_function, result_function in validator:
                value = cls.get_value_from_field(f)
                if not validator_function(value, widget):
                    is_valid = False
            if not is_valid:
                invalid_inputs.append(f.objectName())
        return invalid_inputs

    @classmethod
    def validate_all_fields(cls, widget: FieldWidget):
        function_dict = cls.get_properties().validator_functions.get(widget)
        if not function_dict:
            logging.info(f"No Validator Functions found for widget {widget}")
            return True

        for f, validator in function_dict.items():
            for validator_function, result_function in validator:
                value = cls.get_value_from_field(f)
                is_valid = validator_function(value, widget)
                result_function(f, is_valid)


class DialogTool(FieldTool):
    """Preset for dialog-based (non-live) editing.

    Purpose
    - Reuse FieldTool field management inside a modal dialog. Changes are
      gathered on the widget embedded in the dialog and applied on accept
      rather than immediately.

    Implement in subclasses
    - get_properties() -> DialogProperties with a place to hold the active
      dialog if desired.
    - _get_dialog_class() -> Type[BaseDialog] used to host the field widget.

    Key methods
    - create_dialog(data, parent): Create a field widget and embed it as the
      dialog's content; pre-fill via sync_from_model().
    - validate_dialog(dialog): Check validators via all_inputs_are_valid()
      and accept if OK. Override to add custom validation/feedback.
    - connect_internal_signals(): Ensures the embedded widget is closed when
      the dialog is accepted/declined.

    When to use
    - Prefer DialogTool when users should review changes and explicitly
      confirm them, as opposed to live-editing fields.
    """

    signals = DialogSignals()

    @classmethod
    @abstractmethod
    def get_properties(cls) -> DialogProperties:
        return None

    @classmethod
    @abstractmethod
    def _get_dialog_class(cls) -> Type[BaseDialog]:
        logging.error(f"This function needs to be subclassed")
        return BaseDialog

    @classmethod
    def request_dialog(cls, data: object, parent: QWidget):
        cls.signals.dialog_requested.emit(data, parent)

    @classmethod
    def create_dialog(cls, data: object, parent: QWidget) -> BaseDialog:
        widget = cls.create_widget(data, None)
        dialog = cls._get_dialog_class()(widget, parent)
        cls.sync_from_model(widget, data)
        dialog._layout.insertWidget(0, widget)
        # dialog.new_button.clicked.connect(lambda _, d=dialog: cls.validate_dialog(d))
        cls.get_properties().dialog = dialog
        return dialog

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.dialog_accepted.connect(lambda dialog: dialog._widget.closed.emit())
        cls.signals.dialog_declined.connect(lambda dialog: dialog._widget.closed.emit())
        cls.signals.dialog_requested.connect(lambda d, p: cls._get_trigger().create_dialog(d, p))

    @classmethod
    def connect_widget_signals(cls, widget: FieldWidget):
        super().connect_widget_signals(widget)

    @classmethod
    def connect_dialog_signals(cls, dialog: BaseDialog):
        pass

    @classmethod
    def validate_dialog(cls, dialog: BaseDialog) -> None:
        if cls.all_inputs_are_valid(dialog._widget):
            dialog.accept()
        else:
            pass

    @classmethod
    def get_dialog(cls):
        return cls.get_properties().dialog

    @classmethod
    def get_data(cls):
        widget = cls.get_widget()
        if not widget:
            return None
        return widget.bsdd_data

    @classmethod
    def get_widget(cls, data=None):
        """
        if a dialog is open, return its widget
        otherwise return the widget for the given data object
        some modules can be run as widget or as dialog this handles those edgecases
        if the module is only run as a dialog no data object is needed

        """
        if data is not None:
            return super().get_widget(data)
        dialog = cls.get_dialog()
        if not dialog:
            return super().get_widget(data)
        return dialog._widget


class ItemViewTool(BaseTool):

    signals = ViewSignals()
    # TODO: make info_requested a signal for all handlers

    @classmethod
    @abstractmethod
    def get_properties(cls) -> ViewProperties:
        return None

    @classmethod
    @abstractmethod
    def _get_model_class(cls) -> Type[ItemModel]:
        return None

    @classmethod
    @abstractmethod
    def _get_trigger(cls) -> ModuleType:
        return None

    @classmethod
    @abstractmethod
    def delete_selection(view: ItemViewType):
        return None

    @classmethod
    def _get_proxy_model_class(cls) -> Type[QSortFilterProxyModel]:
        return QSortFilterProxyModel

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.delete_selection_requested.connect(cls.delete_selection)
        cls.signals.model_refresh_requested.connect(cls.reset_views)
        cls.signals.selection_changed.connect(lambda v, d: logging.info(f"Selection changed {v}"))

    @classmethod
    def connect_view_signals(cls, view: QAbstractItemView) -> None:
        view.customContextMenuRequested.connect(
            lambda p: cls._get_trigger().context_menu_requested(view, p)
        )
        sel_model = view.selectionModel()
        sel_model.currentChanged.connect(lambda s, d: cls.on_current_changed(view, s, d))

    @classmethod
    def get_selected(cls, view: ItemViewType) -> list[object]:
        selected_values = list()
        for proxy_index in view.selectionModel().selectedIndexes():
            source_index = view.model().mapToSource(proxy_index)
            value = source_index.internalPointer()
            if value not in selected_values:
                selected_values.append(value)
        return selected_values

    @classmethod
    def create_model(cls, data: object) -> tuple[QSortFilterProxyModel, ItemModel]:
        model = cls._get_model_class()(data)
        cls.get_properties().models.add(model)
        proxy_model = cls._get_proxy_model_class()()
        proxy_model.setSourceModel(model)
        proxy_model.setDynamicSortFilter(True)
        return proxy_model, model

    @classmethod
    def get_model(cls, data: object) -> ItemModel | None:
        model_list = [m for m in cls.get_models() if m.bsdd_data == data]
        if not model_list:
            return None
        if len(model_list) > 1:
            logging.info("Multiple Models for the Same Value found!")
        return model_list[-1]

    @classmethod
    def get_models(cls) -> set[ItemModel]:
        return cls.get_properties().models

    @classmethod
    def remove_model(cls, model: ItemModel):
        if model in cls.get_models():
            cls.get_properties().models.remove(model)

    @classmethod
    def register_view(cls, view: ItemViewType):
        logging.info(f"Register View: {view}")

        cls.get_properties().views.add(view)
        cls.get_properties().context_menu_list[view] = list()

    @classmethod
    def unregister_view(cls, view: ItemViewType):
        logging.info(f"Unregister View: {view}")
        if not view in cls.get_properties().views:
            return
        cls.get_properties().views.remove(view)
        cls.get_properties().context_menu_list.pop(view)

    @classmethod
    def get_views(cls) -> set[ItemViewType]:
        return cls.get_properties().views

    @classmethod
    def reset_views(cls):
        for view in cls.get_views():
            cls.reset_view(view)

    @classmethod
    def reset_view(cls, view: ItemViewType):
        logging.info(f"Reset View {view}")
        proxy_model = view.model()
        if not proxy_model:
            return
        source_model = proxy_model.sourceModel()
        source_model.beginResetModel()
        source_model.endResetModel()

    @classmethod
    def clear_context_menu_list(cls, view: ItemViewType):
        prop = cls.get_properties()
        prop.context_menu_list[view] = list()

    @classmethod
    def add_context_menu_entry(
        cls,
        view: ItemViewType,
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
    def create_context_menu(cls, view: ItemViewType, selected_elements: list) -> QMenu:
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

    @classmethod
    def add_column_to_table(
        cls, model: ItemModel, name: str, get_function: Callable, set_function=None
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
    def get_column_count(cls, model: ItemModel):
        columns = cls.get_properties().columns.get(model)
        return len(columns) if columns else 0

    @classmethod
    def get_column_names(cls, model: ItemModel):
        return [x[0] for x in cls.get_properties().columns.get(model) or []]

    @classmethod
    def value_getter_functions(cls, model: ItemModel):
        """_summary_
        returns the function for the value getter

        """
        return [x[1] for x in cls.get_properties().columns.get(model) or []]

    @classmethod
    def value_setter_functions(cls, model: ItemModel):
        """_summary_
        returns the function for the value setter
        """
        return [x[2] for x in cls.get_properties().columns.get(model) or []]

    @classmethod
    def select_and_expand(cls, bsdd_data: BsddDataType, view: TreeItemView | None = None) -> bool:
        """
        Select the given BsddClass in the class tree view and expand the tree down to it.
        Returns True if the item was found and selected, False otherwise.
        """
        # choose a view if none supplied
        if view is None:
            views = cls.get_views()
            if not views:
                return False
            view = views[0]
        if not isinstance(view, QTreeView):
            return

        top_model = view.model()
        # collect proxy chain from top to bottom
        proxies: list[QSortFilterProxyModel] = []
        model = top_model
        while isinstance(model, QSortFilterProxyModel):
            proxies.append(model)
            model = model.sourceModel()
        source_model = model  # ultimate source model

        # recursively search the source model for the internalPointer == bsdd_class
        def find_in_source(parent: QModelIndex = QModelIndex()) -> QModelIndex:
            row_count = source_model.rowCount(parent)
            for row in range(row_count):
                idx = source_model.index(row, 0, parent)
                if not idx.isValid():
                    continue
                if idx.internalPointer() is bsdd_data:
                    return idx
                found = find_in_source(idx)
                if found.isValid():
                    return found
            return QModelIndex()

        src_index = find_in_source(QModelIndex())
        if not src_index.isValid():
            return False

        # map source index up through proxy chain to the view's model
        proxy_index = src_index
        for p in reversed(proxies):
            proxy_index = p.mapFromSource(proxy_index)

        # expand all parents (from root down to immediate parent)
        parents: list[QModelIndex] = []
        p = proxy_index.parent()
        while p.isValid():
            parents.append(p)
            p = p.parent()
        for parent in reversed(parents):
            view.expand(parent)

        sel_model = view.selectionModel()
        if sel_model is None:
            return False

        # select and make current, then ensure it's visible
        sel_model.clearSelection()
        sel_model.setCurrentIndex(proxy_index, QItemSelectionModel.ClearAndSelect)
        sel_model.select(proxy_index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        view.scrollTo(proxy_index, QAbstractItemView.PositionAtCenter)
        return True

    @classmethod
    def on_current_changed(cls, view: ItemViewType, curr: QModelIndex, prev: QModelIndex):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signals.selection_changed.emit(view, index.internalPointer())

    @classmethod
    def request_delete_selection(cls, view):
        cls.signals.delete_selection_requested.emit(view)
