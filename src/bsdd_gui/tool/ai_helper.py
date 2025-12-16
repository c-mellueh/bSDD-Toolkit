from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_gui.module.ai_helper import ui, constants
import bsdd_gui
from bsdd_json import BsddClass
from openai import OpenAI
from bsdd_gui import tool
import json
import os

if TYPE_CHECKING:
    from bsdd_gui.module.ai_helper.prop import AiHelperProperties


class AiHelper:
    @classmethod
    def get_properties(cls) -> AiHelperProperties:
        return bsdd_gui.AiHelperProperties

    @classmethod
    def set_settings_widget(cls, widget: ui.SettingsWidget):
        cls.get_properties().settings_widget = widget

    @classmethod
    def get_settings_widget(cls) -> ui.SettingsWidget | None:
        return cls.get_properties().settings_widget

    @classmethod
    def get_checkstate(cls):
        return tool.Appdata.get_bool_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE)

    @classmethod
    def get_api_key(cls):
        return tool.Appdata.get_string_setting(constants.AI_HELPER_SECTION, constants.API_KEY, "")

    @classmethod
    def get_language(cls):
        return tool.Appdata.get_string_setting(
            constants.AI_HELPER_SECTION, constants.LANGUAGE, constants.LANGUAGE_EN
        )

    @classmethod
    def read_checkstate(cls, widget: ui.SettingsWidget) -> bool:
        return widget.checkBox.isChecked()

    @classmethod
    def read_api_key(cls, widget: ui.SettingsWidget) -> str:
        return widget.lineEdit.text()

    @classmethod
    def read_language(cls, widget: ui.SettingsWidget) -> str:
        return widget.cb_language.currentText()

    @classmethod
    def build_class_instructions(cls, lang: str) -> str:
        if lang == constants.LANGUAGE_DE:
            return (
                "Du bist ein erfahrener BIM-Manager und bSDD-Redakteur. "
                "Formuliere eine technisch-neutrale Definition der bSDD-Klasse in genau 2–3 Sätzen. "
                "Keine Aufzählungen, keine Beispiele, keine Metakommentare. "
                "Nutze die JSON-Informationen (Name, Beschreibung, Synonyme, Parent/Child, Properties etc.) "
                "nur soweit vorhanden; wenn Details fehlen, bleibe allgemein und erfinde nichts."
            )
        if lang == constants.LANGUAGE_EN:
            return (
                "You are an experienced BIM manager and bSDD editor. "
                "Write a technically neutral definition of the bSDD class in exactly 2–3 sentences. "
                "No bullet points, no examples, no meta commentary. "
                "Use the JSON information (name, description, synonyms, parent/child, properties, etc.) "
                "only if present; if details are missing, stay general and do not invent facts."
            )
        raise ValueError(f"Unsupported language. Use one of {constants.LANGUAGES}")

    def build_user_input(bsdd_class: BsddClass, lang: str) -> str:
        # Komplette Klasse mitsenden, damit das Modell alle vorhandenen Infos nutzen kann.
        # Das Script ist absichtlich schema-agnostisch.
        if lang == "de":
            header = "Hier ist eine bSDD-Klasse als JSON. Definiere diese Klasse:"
        else:
            header = "Here is a bSDD class as JSON. Define this class:"

        dump: dict = bsdd_class.model_dump(ensure_ascii=False, indent=2)
        relevant_keys = ["Name", "ParentClassCode", "RelatedIfcEntityNamesList", "ClassProperties"]
        reduced_dump = {key: dump.get(key) for key in relevant_keys}

        return header + "\n\n" + json.dumps(reduced_dump, ensure_ascii=True)

    @classmethod
    def generate_class_definition(
        cls,
        bsdd_class: BsddClass,
        api_key=None,
        language=None,
        model="gpt-4o-mini",
        max_output_tokens=220,
    ):
        api_key = cls.get_api_key()
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("ERROR: API-Key ist nicht gesetzt.")
            return None

        if not language:
            language = cls.get_language()

        client = OpenAI(api_key=api_key)
        instructions = cls.build_class_instructions(language)
        user_input = cls.build_user_input(bsdd_class, language)

        try:
            resp = client.responses.create(
                model=model,
                instructions=instructions,
                input=user_input,
                max_output_tokens=max_output_tokens,
            )
        except Exception as e:
            logging.error(f"API-Request fehlgeschlagen: {e}")
            return None
        text_chunks = []
        for item in getattr(resp, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                if getattr(content, "type", None) == "output_text":
                    text_chunks.append(getattr(content, "text", ""))

        out = "\n".join([t for t in text_chunks if t]).strip()
        if not out:
            # Fallback (falls SDK-Struktur sich unterscheidet)
            out = getattr(resp, "output_text", "") or str(resp)
        return out
