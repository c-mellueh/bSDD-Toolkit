from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal, QObject
import bsdd_gui
from bsdd_gui.presets.tool_presets import ViewSignaller
from bsdd_parser import BsddClass
from bsdd_gui.module.class_editor import trigger, ui

if TYPE_CHECKING:
    from bsdd_gui.module.class_editor.prop import ClassEditorProperties


class Signaller:
    class_info_requested = Signal(BsddClass)


class ClassEditor:
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassEditorProperties:
        return bsdd_gui.ClassEditorProperties

    @classmethod
    def connect_signaller(cls):
        cls.signaller.class_info_requested.connect(trigger.open_class_editor)

    @classmethod
    def create_widget(cls, bsdd_class: BsddClass):
        widget = ui.ClassEditor(bsdd_class)
        return widget
