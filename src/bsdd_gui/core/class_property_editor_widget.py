from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClassProperty
from bsdd_gui.module.class_property_editor_widget.constants import (
    SEPERATOR_SECTION,
    SEPERATOR,
    SEPERATOR_STATUS,
)
from PySide6.QtCore import QCoreApplication
from bsdd_gui.module.class_property_editor_widget import ui, views, constants

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_editor_widget import ui as property_editor_ui


def connect_signals(
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    property_table: Type[tool.ClassPropertyTableView],
    main_window: Type[tool.MainWindowWidget],
    property_editor: Type[tool.PropertyEditorWidget],
    project: Type[tool.Project],
):
    class_property_editor.connect_internal_signals()
    property_table.signals.property_info_requested.connect(
        lambda d: class_property_editor.signals.widget_requested.emit(d, main_window.get())
    )
    main_window.signals.new_property_requested.connect(
        class_property_editor.signals.create_new_class_property_requested.emit
    )
    property_editor.signals.field_changed.connect(class_property_editor.handle_field_changed)
    property_editor.signals.new_property_created.connect(
        lambda _: class_property_editor.validate_widgets()
    )

    def validate_widgets():
        for widget in class_property_editor.get_widgets():
            class_property_editor.validate_all_fields(widget)

    project.signals.property_added.connect(lambda _: validate_widgets())
    project.signals.property_removed.connect(lambda _: validate_widgets())


def retranslate_ui(class_property_editor: Type[tool.ClassPropertyEditorWidget]):
    # TODO
    pass


def create_widget(
    bsdd_class_property: BsddClassProperty,
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    class_property_editor.show_widget(bsdd_class_property, main_window.get(), project.get())


def register_widget(
    widget: ui.ClassPropertyEditor, class_property_editor: Type[tool.ClassPropertyEditorWidget]
):
    class_property_editor.register_widget(widget)
    widget.tv_allowed_values.model().sourceModel().bsdd_data = widget.bsdd_data


def register_fields(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    project: Type[tool.Project],
):
    class_property_editor.register_basic_field(widget, widget.le_code, "Code")
    class_property_editor.register_basic_field(widget, widget.te_description, "Description")
    class_property_editor.register_basic_field(widget, widget.cb_is_required, "IsRequired")

    ### Property Reference Field
    class_property_editor.register_field_getter(
        widget, widget.le_property_reference, class_property_editor.get_property_reference
    )
    class_property_editor.register_field_setter(
        widget,
        widget.le_property_reference,
        lambda e, v, p=project: class_property_editor.set_property_reference(e, v, p.get()),
    )
    class_property_editor.register_field_listener(widget, widget.le_property_reference)


def register_validators(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    wi = widget
    class_property_editor.add_validator(
        wi,
        wi.le_property_reference,
        lambda v, w, p=project: class_property_editor.is_property_reference_valid(
            v, w.bsdd_data, p.get()
        ),
        lambda w, v: util.set_invalid(w, not v),
    )

    class_property_editor.add_validator(
        wi,
        wi.le_property_reference,
        lambda v, w, p=project: class_property_editor.is_property_reference_valid(
            v, w.bsdd_data, p.get()
        ),
        lambda f, v, w=wi: class_property_editor.handle_property_reference_button(w, f, v),
    )


def connect_widget(
    widget: ui.ClassPropertyEditor, class_property_editor: Type[tool.ClassPropertyEditorWidget]
):
    class_property_editor.sync_from_model(widget, widget.bsdd_data)
    class_property_editor.connect_widget_signals(widget)
    class_property_editor.request_property_specific_redraw(widget)


def update_property_specific_fields(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    allowed_value_table: Type[tool.AllowedValuesTableView],
):
    if not widget:
        return
    class_property_editor.update_description_placeholder(widget)
    class_property_editor.update_allowed_units(widget)
    class_property_editor.update_value_view(widget)
    allowed_value_table.reset_view(allowed_value_table.get_view_from_property_editor(widget))


def create_dialog(
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
    property_set_table: Type[tool.PropertySetTableView],
):
    bsdd_class = main_window.get_active_class()
    property_set = main_window.get_active_pset()
    if bsdd_class is None or property_set is None:
        return

    # Create Placeholder Class Property
    pset_was_temporary = property_set_table.is_temporary_pset(bsdd_class, property_set)
    bsdd_class_property = class_property_editor.create_temporary_property(property_set, bsdd_class)

    # Create Dialog
    dialog = class_property_editor.create_dialog(
        bsdd_class_property, main_window.get(), project.get()
    )
    text = QCoreApplication.translate("ClassPropertyEditor", "Create New Class Property")
    dialog.setWindowTitle(text)

    if dialog.exec():
        class_property_editor.sync_to_model(dialog._widget, bsdd_class_property)
        # add ClassProperty to Class
        class_property_editor.signals.new_class_property_created.emit(bsdd_class_property)
        # bsdd_class_property.parent().ClassProperties.append(bsdd_class_property)

        if pset_was_temporary:
            property_set_table.remove_temporary_pset(bsdd_class_property.parent(), property_set)
            property_set_table.signals.model_refresh_requested.emit()

        class_property_editor.signals.dialog_accepted.emit(dialog)
    else:
        class_property_editor.signals.dialog_declined.emit(dialog)


#### Settings


def fill_settings(func, settings: Type[tool.SettingsWidget]):
    settings.add_page_to_toolbox(views.SplitterSettings, "pageSplitter", func)


def setup_splitter_settings(
    widget: views.SplitterSettings,
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    appdata: Type[tool.Appdata],
):
    class_property_editor.set_splitter_settings_widget(widget)
    splitter = appdata.get_string_setting(constants.SEPERATOR_SECTION, constants.SEPERATOR, ";")
    is_active = appdata.get_bool_setting(constants.SEPERATOR_SECTION, constants.SEPERATOR_STATUS)
    widget.line_edit_seperator.setText(splitter)
    widget.check_box_seperator.setChecked(is_active)


def splitter_settings_accepted(
    class_property_editor: Type[tool.ClassPropertyEditorWidget], appdata: Type[tool.Appdata]
):
    widget = class_property_editor.get_splitter_settings_widget()
    is_seperator_activated = class_property_editor.get_splitter_settings_checkstate(widget)
    text = class_property_editor.get_splitter_settings_text(widget)
    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")
    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR, text)
    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, is_seperator_activated)
    if not text:
        appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, False)
