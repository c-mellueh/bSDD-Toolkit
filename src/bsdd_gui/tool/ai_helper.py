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
    def get_client(cls):
        client = cls.get_properties().client
        if not client:
            client = cls.load_client()
            cls.get_properties().client = client
        return client

    @classmethod
    def load_client(cls, api_key=None):
        if not api_key:
            api_key = cls.get_api_key()
        if not api_key:
            return None
        client = OpenAI(api_key=api_key)
        return client

    @classmethod
    def get_settings_widget(cls) -> ui.SettingsWidget | None:
        return cls.get_properties().settings_widget

    @classmethod
    def get_checkstate(cls):
        return tool.Appdata.get_bool_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE)

    @classmethod
    def get_api_key(cls):
        api_key = tool.Appdata.get_string_setting(
            constants.AI_HELPER_SECTION, constants.API_KEY, ""
        )
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        return api_key

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
                "Du bist ein erfahrener BIM-Manager und Fachexperte für Infrastruktur- und Ingenieurbauwerke."
                "Du erhältst eine einzelne bSDD-Klasse im JSON-Format gemäß buildingSMART-Struktur."
                "Aufgabe:"
                "Erstelle eine fachlich korrekte, prägnante Definition der Klasse in deutscher Sprache."
                "Regeln für die Definition:"
                "Umfang: 3-5 vollständige Sätze"
                "Stil: technisch-neutral, sachlich, normnah"
                "Beschreibe:"
                "die baukonstruktive Ausführung"
                "den primären Zweck / die Funktion"
                "typische Einsatzbereiche"
                "Wenn fachlich sinnvoll, nenne einschlägige Normen oder Regelwerke (z. B. DIN, EN), ohne diese zu erklären"
                "Nutze keine Aufzählungen"
                "Wiederhole keine JSON-Feldnamen und zähle keine Eigenschaften oder Beispielwerte auf"
                "Verwende keine Einleitungssätze wie „Diese Klasse beschreibt …“"
                "Ausgabe:"
                "Gib ausschließlich die formulierte Klassendefinition als Fließtext zurück, ohne Zusatzkommentare oder Hinweise."
            )
        if lang == constants.LANGUAGE_EN:
            return (
                "You are an experienced BIM manager and a specialist in infrastructure and civil engineering projects."
                "You will receive a single bSDD class in JSON format according to the buildingSMART structure."
                "Task:"
                "Create a technically correct, concise definition of the class in German."
                "You are an experienced BIM manager and a specialist in infrastructure and civil engineering projects."
                "You will receive a single bSDD class in JSON format according to the buildingSMART structure ..." 
                "Rules for the definition:"
                "Length: 3-5 complete sentences"
                "Style: technical-neutral, factual, and standards-compliant"
                "Describe:"
                "the structural design"
                "the primary purpose/function"
                "typical areas of application"
                "If technically relevant, mention applicable standards or regulations (e.g., DIN, EN) without explaining them"
                "Do not use bullet points"
                "Do not repeat JSON field names or list properties or example values"
                "Do not use introductory sentences such as „This class describes…“"
                "Output:"
                "Return only the formulated class definition as plain text, without additional comments or notes."
            )
        raise ValueError(f"Unsupported language. Use one of {constants.LANGUAGES}")

    def build_user_input(json_text: str, lang: str) -> str:
        # Komplette Klasse mitsenden, damit das Modell alle vorhandenen Infos nutzen kann.
        # Das Script ist absichtlich schema-agnostisch.
        if lang == constants.LANGUAGE_DE:
            header = "Hier ist eine bSDD-Klasse als JSON. Definiere diese Klasse:"
        else:
            header = "Here is a bSDD class as JSON. Define this class:"
        text = header + "\n\n" + json_text
        print(text)
        return text

    @classmethod
    def generate_class_definition(
        cls,
        json_text: str,
        api_key=None,
        language=None,
        model="gpt-4o-mini",
        max_output_tokens=220,
    ):
        api_key = cls.get_api_key()

        if not api_key:
            logging.error("ERROR: API-Key ist nicht gesetzt.")
            return None

        if not language:
            language = cls.get_language()

        client = OpenAI(api_key=api_key)
        instructions = cls.build_class_instructions(language)
        user_input = cls.build_user_input(json_text, language)

        try:
            resp = client.responses.create(
                model=model,
                instructions=instructions,
                input=user_input,
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
