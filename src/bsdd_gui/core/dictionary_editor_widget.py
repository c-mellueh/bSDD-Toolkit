from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QWidget

from PySide6.QtGui import QCloseEvent
from bsdd_json import BsddDictionary
from bsdd_gui.module.dictionary_editor_widget.constants import LANGUAGE_ISO_CODES
import qtawesome as qta

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.dictionary_editor_widget import ui


def connect_signals(
    dictionary_editor: Type[tool.DictionaryEditorWidget], project: Type[tool.Project]
):
    dictionary_editor.connect_internal_signals()

    def handle_field_change(widget, field):
        name = dictionary_editor.get_name_from_field(widget, field)
        value = dictionary_editor.get_value_from_field(field)
        project.signals.data_changed.emit(name, value)

    dictionary_editor.signals.field_changed.connect(handle_field_change)


def retranslate_ui(
    dictionary_editor: Type[tool.DictionaryEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    """Retranslates the UI elements of dictionary Editor. and the Actions."""
    action = dictionary_editor.get_action(main_window.get(), "open_window")
    text = QCoreApplication.translate("DictionaryEditor", "Dictionary Data")
    action.setText(text)
    title = util.get_window_title(
        QCoreApplication.translate("DictionaryEditor", " bSDD-Dictionary")
    )
    for widget in dictionary_editor.get_widgets():
        widget.setWindowTitle(title)


def create_widget(
    bsdd_dictionary: BsddDictionary,
    parent_widget: QWidget | None,
    dictionary_editor: Type[tool.DictionaryEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    if parent_widget is None:
        parent_widget = main_window.get()
    dictionary_editor.show_widget(bsdd_dictionary, parent_widget)
    retranslate_ui(dictionary_editor, main_window, util)


def register_widget(
    widget: ui.DictionaryEditor, dictionary_editor: Type[tool.DictionaryEditorWidget]
):
    dictionary_editor.register_widget(widget)


def connect_to_main_window(
    dictionary_editor: Type[tool.DictionaryEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
) -> None:
    action = main_window.add_action(
        "menuData",
        "Dictionary Data",
        lambda: dictionary_editor.request_widget(project.get(), main_window.get()),
        qta.icon("mdi6.book-alphabet"),
    )
    dictionary_editor.set_action(main_window.get(), "open_window", action)


def register_fields(
    widget: ui.DictionaryEditor, dictionary_editor: Type[tool.DictionaryEditorWidget]
):

    dictionary_editor.register_basic_field(widget, widget.le_org_code, "OrganizationCode")
    dictionary_editor.register_basic_field(widget, widget.le_dictionary_code, "DictionaryCode")
    dictionary_editor.register_basic_field(widget, widget.le_dictionary_name, "DictionaryName")
    dictionary_editor.register_basic_field(
        widget, widget.le_dictionary_version, "DictionaryVersion"
    )
    dictionary_editor.register_basic_field(widget, widget.cb_language_only, "LanguageOnly")
    dictionary_editor.register_basic_field(widget, widget.cb_use_own_uri, "UseOwnUri")
    dictionary_editor.register_basic_field(widget, widget.le_dictionary_uri, "DictionaryUri")
    dictionary_editor.register_basic_field(widget, widget.le_license, "License")
    dictionary_editor.register_basic_field(widget, widget.le_license_url, "LicenseUrl")
    dictionary_editor.register_basic_field(
        widget, widget.le_change_request_mail, "ChangeRequestEmailAddress"
    )
    dictionary_editor.register_basic_field(widget, widget.cb_model_version, "ModelVersion")
    dictionary_editor.register_basic_field(widget, widget.le_more_info, "MoreInfoUrl")
    dictionary_editor.register_basic_field(
        widget, widget.le_qa_procedure, "QualityAssuranceProcedure"
    )
    dictionary_editor.register_basic_field(
        widget, widget.le_qa_procedure_url, "QualityAssuranceProcedureUrl"
    )
    dictionary_editor.register_basic_field(widget, widget.de_release_date, "ReleaseDate")
    dictionary_editor.register_basic_field(widget, widget.cb_status, "Status")

    widget.cb_language_iso.addItems(LANGUAGE_ISO_CODES)
    dictionary_editor.register_basic_field(widget, widget.cb_language_iso, "LanguageIsoCode")


def register_validators(
    widget: ui.DictionaryEditor,
    dictionary_editor: Type[tool.DictionaryEditorWidget],
    util: Type[tool.Util],
):
    dictionary_editor.add_validator(
        widget,
        widget.le_dictionary_code,
        dictionary_editor.is_dictionary_code_valid,
        lambda w, v: util.set_invalid(w, not v),
    )
    dictionary_editor.add_validator(
        widget,
        widget.le_org_code,
        dictionary_editor.is_org_code_valid,
        lambda w, v: util.set_invalid(w, not v),
    )
    dictionary_editor.add_validator(
        widget,
        widget.le_dictionary_name,
        dictionary_editor.is_dictionary_name_valid,
        lambda w, v: util.set_invalid(w, not v),
    )

    dictionary_editor.add_validator(
        widget,
        widget.le_dictionary_version,
        dictionary_editor.is_dictionary_version_valid,
        lambda w, v: util.set_invalid(w, not v),
    )
    dictionary_editor.add_validator(
        widget,
        widget.cb_language_iso,
        dictionary_editor.is_language_iso_valid,
        lambda w, v: util.set_invalid(w, not v),
    )
    dictionary_editor.add_validator(
        widget,
        widget.le_dictionary_uri,
        dictionary_editor.is_dictionary_uri_valid,
        lambda w, v: util.set_invalid(w, not v),
    )
    dictionary_editor.add_validator(
        widget,
        widget.cb_use_own_uri,
        lambda _, w: dictionary_editor.is_dictionary_uri_valid(w.le_dictionary_uri.text(), w),
        lambda _, v, w=widget.le_dictionary_uri: util.set_invalid(w, not v),
    )


def connect_widget(
    widget: ui.DictionaryEditor, dictionary_editor: Type[tool.DictionaryEditorWidget]
):
    dictionary_editor.connect_widget_signals(widget)


def remove_widget(
    widget: ui.DictionaryEditor,
    event: QCloseEvent,
    dictionary_editor: Type[tool.DictionaryEditorWidget],
    popups: Type[tool.Popups],
):
    if not dictionary_editor.all_inputs_are_valid(widget):
        event.ignore()
        text = QCoreApplication.translate("Project", "Required Inputs are missing!")
        missing_text = QCoreApplication.translate("Project", "is mssing")
        missing_inputs = dictionary_editor.get_invalid_inputs(widget)
        popups.create_warning_popup(
            f" {missing_text}\n".join(missing_inputs) + f" {missing_text}", None, text
        )
    else:
        event.accept()
