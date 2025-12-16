from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import Signal, QObject, QThread, Qt
from PySide6.QtWidgets import QToolButton
import qtawesome as qta

import logging
from bsdd_gui.module.ai_helper import ui, constants, trigger
import bsdd_gui
from bsdd_json import BsddClass
from openai import OpenAI
from bsdd_gui import tool
import json
import os

if TYPE_CHECKING:
    from bsdd_gui.module.ai_helper.prop import (
        AiHelperProperties,
        AiClassDescriptionProperties,
        AiPropertyDescriptionProperties,
    )
    from bsdd_gui.module.class_editor_widget import ui as class_edit_ui
from bsdd_gui.module.property_editor_widget import ui as property_ui
from bsdd_gui.module.class_property_editor_widget import ui as class_property_ui


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


class AiClassDescription:
    @classmethod
    def get_properties(cls) -> AiClassDescriptionProperties:
        return bsdd_gui.AiClassDescriptionProperties

    @classmethod
    def add_ai_to_classedit(cls, widget: class_edit_ui.ClassEditor):
        """Place a helper button inside the definition text edit."""
        widget._ai_button = QToolButton(widget.te_definition.viewport())
        widget._ai_button.setIcon(qta.icon("mdi6.creation-outline"))
        widget._ai_button.setAutoRaise(True)
        widget._ai_button.setCursor(Qt.PointingHandCursor)
        widget.te_definition.textChanged.connect(lambda: cls._sync_ai_button(widget))
        cls._position_ai_button(widget)
        cls._sync_ai_button(widget)
        widget._ai_button.clicked.connect(lambda: trigger.generate_class_definition(widget))

    @classmethod
    def _position_ai_button(cls, widget) -> None:
        margin = 6
        widget._ai_button.move(margin, margin)

    @classmethod
    def _sync_ai_button(cls, widget) -> None:
        is_empty = widget.te_definition.toPlainText() == ""
        widget._ai_button.setVisible(is_empty)

    @classmethod
    def build_class_instructions(cls, lang: str) -> str:
        if lang == constants.LANGUAGE_DE:
            return "Du bist ein erfahrener BIM-Manager und Fachexperte für Infrastruktur- und Ingenieurbauwerke. Du erhältst eine einzelne bSDD-Klasse im JSON-Format gemäß der buildingSMART-Struktur. Deine Aufgabe ist es, eine fachlich korrekte, prägnante und technisch neutrale Definition dieser Klasse in deutscher Sprache zu verfassen. Der Text besteht aus drei bis fünf vollständigen Sätzen im normnahen Stil. Die Definition umfasst baukonstruktive Ausführung, primären Zweck bzw. Funktion sowie typische Einsatzbereiche. Falls fachlich sinnvoll, können einschlägige Normen wie DIN oder EN benannt werden, jedoch ohne nähere Erläuterung. Verzichte auf Aufzählungen, Wiederholung von JSON-Feldnamen, Eigenschaften, Beispielwerte sowie Einleitungssätze wie „Diese Klasse beschreibt …“. Gib ausschließlich die formulierte Klassendefinition als zusammenhängenden Fließtext ohne Zusatzkommentare oder Hinweise zurück."
        if lang == constants.LANGUAGE_EN:
            return "You are an experienced BIM manager and expert in infrastructure and civil engineering structures. You will receive a single bSDD class in JSON format according to the buildingSMART structure. Your task is to write a technically correct, concise, and neutral definition of this class in German. The text should consist of three to five complete sentences in a style close to the standards. The definition should include structural design, primary purpose or function, and typical areas of application. Where technically appropriate, relevant standards such as DIN or EN may be mentioned, but without further explanation. Avoid bullet points, repetition of JSON field names, properties, example values, and introductory sentences such as 'This class describes…'. Return only the formulated class definition as a continuous text without additional comments or notes."
        raise ValueError(f"Unsupported language. Use one of {constants.LANGUAGES}")

    def build_user_input(json_text: str, lang: str) -> str:
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
        client=None,
    ):
        if not api_key:
            logging.error("ERROR: API-Key ist nicht gesetzt.")
            return None

        if not language:
            language = constants.LANGUAGE_EN

        if client is None:
            client = OpenAI(api_key=api_key)
        instructions = cls.build_class_instructions(language)
        user_input = cls.build_user_input(json_text, language)

        try:
            resp = client.responses.create(
                model=model,
                instructions=instructions,
                input=user_input,
                text={"verbosity": "low"},
                reasoning={"effort": "minimal"},
                store=True,
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

    @classmethod
    def create_gen_def_thread(cls, *args, **kwargs):
        class _SetupWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                value = cls.generate_class_definition(*args, **kwargs)
                self.finished.emit(value)

        ai_worker = _SetupWorker()
        cls.get_properties().ai_worker = ai_worker
        ai_thread = QThread()

        cls.get_properties().ai_thread = ai_thread
        ai_worker.moveToThread(ai_thread)
        ai_worker.finished.connect(ai_thread.quit)
        ai_worker.finished.connect(ai_worker.deleteLater)
        ai_worker.error.connect(ai_thread.quit)
        ai_worker.error.connect(ai_worker.deleteLater)
        ai_thread.finished.connect(ai_thread.deleteLater)
        ai_thread.started.connect(ai_worker.run, Qt.ConnectionType.QueuedConnection)
        return ai_worker, ai_thread

