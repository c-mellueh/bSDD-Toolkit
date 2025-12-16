from __future__ import annotations
from bsdd_gui.module.ai_helper import ui, constants
from typing import TYPE_CHECKING, Type
import json
from bsdd_json import BsddClass, BsddClassProperty
from PySide6.QtCore import QModelIndex, QCoreApplication, QTimer
from bsdd_gui.presets.ui_presets.waiting import start_waiting_widget, stop_waiting_widget
from bsdd_json.utils import property_utils as prop_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_editor_widget import ui as class_edit_ui
from bsdd_gui.module.property_editor_widget import ui as property_ui
from bsdd_gui.module.class_property_editor_widget import ui as class_property_ui


def fill_settings(func, settings: Type[tool.SettingsWidget]):
    settings.add_page_to_toolbox(ui.SettingsWidget, "pageAI", func)


def connect_signals(
    ai_helper: Type[tool.AiHelper],
    ai_class: Type[tool.AiClassDescription],
    ai_property: Type[tool.AiPropertyDescription],
    class_editor: Type[tool.ClassEditorWidget],
    property_editor: Type[tool.PropertyEditorWidget],
    class_property_editor: Type[tool.PropertyEditorWidget],
):
    if not ai_helper.get_checkstate():
        return
    class_editor.signals.widget_created.connect(ai_class.add_ai_to_classedit)
    property_editor.signals.widget_created.connect(ai_property.add_ai_to_propertyedit)
    class_property_editor.signals.widget_created.connect(ai_property.add_ai_to_propertyedit)


def setup_settings(
    widget: ui.SettingsWidget,
    ai_helper: Type[tool.AiHelper],
    appdata: Type[tool.Appdata],
):
    ai_helper.set_settings_widget(widget)
    splitter = appdata.get_string_setting(constants.AI_HELPER_SECTION, constants.API_KEY, "")
    language = appdata.get_string_setting(constants.AI_HELPER_SECTION, constants.LANGUAGE, "")
    is_active = appdata.get_bool_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE)
    sentence_count = appdata.get_int_setting(
        constants.AI_HELPER_SECTION, constants.SENTENCE_COUNT, 3
    )

    widget.lineEdit.setText(splitter)
    widget.checkBox.setChecked(is_active)
    widget.cb_language.setCurrentText(language)
    widget.spinBox.setValue(sentence_count)


def splitter_settings_accepted(ai_helper: Type[tool.AiHelper], appdata: Type[tool.Appdata]):
    widget = ai_helper.get_settings_widget()
    is_seperator_activated = ai_helper.read_checkstate(widget)
    text = ai_helper.read_api_key(widget)
    language = ai_helper.read_language(widget)
    sentence_count = ai_helper.read_sentence_count(widget)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.API_KEY, text)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE, is_seperator_activated)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.LANGUAGE, language)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.SENTENCE_COUNT, sentence_count)

    if not text:
        appdata.set_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE, False)


def generate_class_definition(
    widget: class_edit_ui.ClassEditor,
    class_editor: Type[tool.ClassEditorWidget],
    ai_helper: Type[tool.AiHelper],
    ai_class: Type[tool.AiClassDescription],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    bsdd_class = class_editor.get_data()
    dump = dict()
    if isinstance(bsdd_class, BsddClass):
        dump = bsdd_class.model_dump()
    dump["Name"] = widget.le_name.text()
    dump["RelatedIfcEntityNamesList"] = widget.ti_related_ifc_entity.tags()
    relevant_keys = ["Name", "ParentClassCode", "RelatedIfcEntityNamesList"]

    reduced_dump = {key: dump.get(key) for key in relevant_keys}
    json_text = json.dumps(reduced_dump)
    widget._ai_button.hide()
    waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(
        "Generating Definition", parent_widget=widget.te_definition
    )

    api_key = ai_helper.get_api_key()
    language = ai_helper.get_language()
    model = ai_helper.get_model()
    max_output_tokens = ai_helper.get_output_tokens()
    client = ai_helper.get_client()
    sentence_count = ai_helper.get_sentence_count()

    ai_worker, ai_thread = ai_class.create_gen_def_thread(
        json_text, api_key, language, model, max_output_tokens, client,sentence_count
    )

    def _finished(definition):
        if definition:
            QTimer.singleShot(0, widget, lambda: widget.te_definition.setText(definition))
        else:
            QTimer.singleShot(0, widget, lambda: widget._ai_button.show())
        stop_waiting_widget(waiting_worker)

    ai_worker.finished.connect(_finished)
    ai_thread.start()


def generate_property_definition(
    widget: property_ui.PropertyEditor | class_property_ui.ClassPropertyEditor,
    ai_helper: Type[tool.AiHelper],
    ai_property: Type[tool.AiPropertyDescription],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindowWidget],
    util: Type[tool.Util],
):
    if isinstance(widget, property_ui.PropertyEditor):
        data = {"Name": widget.le_name.text()}
        text_widget = widget.te_definition
    else:
        element: BsddClassProperty = widget.bsdd_data
        text_widget = widget.te_description
        if not element:
            bsdd_class = main_window.get_active_class()
            name = widget.le_code.text()
        else:
            bsdd_class = element.parent()
            name = prop_utils.get_name(element, project.get())
        data = {"Name": name, "ParentClass": bsdd_class.Name}
    json_text = json.dumps(data)
    widget._ai_button.hide()
    waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(
        "Generating Definition", parent_widget=text_widget
    )

    api_key = ai_helper.get_api_key()
    language = ai_helper.get_language()
    model = ai_helper.get_model()
    max_output_tokens = ai_helper.get_output_tokens()
    client = ai_helper.get_client()
    sentence_count = ai_helper.get_sentence_count()
    ai_worker, ai_thread = ai_property.create_gen_def_thread(
        json_text, api_key, language, model, max_output_tokens, client, sentence_count
    )

    def _finished(definition):
        text_widget = ai_property.get_text_widget(widget)
        if definition:
            QTimer.singleShot(0, widget, lambda: text_widget.setText(definition))
        else:
            QTimer.singleShot(0, widget, lambda: widget._ai_button.show())
        stop_waiting_widget(waiting_worker)

    ai_worker.finished.connect(_finished)
    ai_thread.start()
