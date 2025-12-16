from __future__ import annotations
from bsdd_gui.module.ai_helper import ui, constants
from typing import TYPE_CHECKING, Type
import json
from bsdd_json import BsddClass
from PySide6.QtCore import QModelIndex, QCoreApplication, QTimer
from bsdd_gui.presets.ui_presets.waiting import start_waiting_widget, stop_waiting_widget
from bsdd_json.utils import property_utils as prop_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_editor_widget import ui as class_edit_ui




def fill_settings(func, settings: Type[tool.SettingsWidget]):
    settings.add_page_to_toolbox(ui.SettingsWidget, "pageGeneral", func)

def connect_signals(ai_helper:Type[tool.AiHelper],class_editor:Type[tool.ClassEditorWidget]):
    class_editor.signals.widget_created.connect(ai_helper.add_ai_to_classedit)

def setup_settings(
    widget: ui.SettingsWidget,
    ai_helper: Type[tool.AiHelper],
    appdata: Type[tool.Appdata],
):
    ai_helper.set_settings_widget(widget)
    splitter = appdata.get_string_setting(constants.AI_HELPER_SECTION, constants.API_KEY, "")
    language = appdata.get_string_setting(constants.AI_HELPER_SECTION, constants.LANGUAGE, "")
    is_active = appdata.get_bool_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE)
    widget.lineEdit.setText(splitter)
    widget.checkBox.setChecked(is_active)
    widget.cb_language.setCurrentText(language)


def splitter_settings_accepted(ai_helper: Type[tool.AiHelper], appdata: Type[tool.Appdata]):
    widget = ai_helper.get_settings_widget()
    is_seperator_activated = ai_helper.read_checkstate(widget)
    text = ai_helper.read_api_key(widget)
    language = ai_helper.read_language(widget)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.API_KEY, text)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE, is_seperator_activated)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.LANGUAGE, language)
    
    if not text:
        appdata.set_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE, False)

def create_ai_definition(
    widget: class_edit_ui.ClassEditor,
    class_editor: Type[tool.ClassEditorWidget],
    ai_helper: Type[tool.AiHelper],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    bsdd_class = class_editor.get_data()
    dump = dict()
    if isinstance(bsdd_class, BsddClass):
        dump = bsdd_class.model_dump()
    dump["Name"] = widget.le_name.text()
    dump["RelatedIfcEntityNamesList"] = widget.ti_related_ifc_entity.tags()
    relevant_keys = ["Name", "ParentClassCode", "RelatedIfcEntityNamesList", "ClassProperties"]
    reduced_class_properties = [
        prop_utils.get_name(cp, project.get()) for cp in bsdd_class.ClassProperties or []
    ]
    dump["ClassProperties"] = reduced_class_properties
    reduced_dump = {key: dump.get(key) for key in relevant_keys}
    json_text = json.dumps(reduced_dump)
    widget._definition_toolbutton.hide()
    waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(
        "Generating Definition", parent_widget=widget.te_definition
    )
    ai_worker, ai_thread = ai_helper.create_gen_def_thread(json_text)

    def _finished(definition):
        if definition:
            QTimer.singleShot(0, widget, lambda: widget.te_definition.setText(definition))
        else:
            QTimer.singleShot(0, widget, lambda: widget._definition_toolbutton.show())
        stop_waiting_widget(waiting_worker)

    ai_worker.finished.connect(_finished)
    ai_thread.start()
