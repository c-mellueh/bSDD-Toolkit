from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import logging


import bsdd_gui
from bsdd_parser import BsddProperty, BsddClass, BsddDictionary
from bsdd_gui.presets.tool_presets import ViewHandler, ViewSignaller
from bsdd_parser.utils import bsdd_dictionary as dict_utils
from bsdd_parser.utils import bsdd_class as cl_utils
from bsdd_parser.utils import bsdd_class_property as prop_utils

if TYPE_CHECKING:
    from bsdd_gui.module.relationship_editor.prop import RelationshipEditorProperties
from bsdd_gui.module.relationship_editor import ui, trigger


class Signaller(ViewSignaller):
    pass


class RelationshipEditor(ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> RelationshipEditorProperties:
        return bsdd_gui.RelationshipEditorProperties

    @classmethod
    def init_widget(
        cls,
        widget: ui.RelationshipWidget,
        data: BsddProperty | BsddClass,
        mode: Literal["dialog"] | Literal["live"] = "dialog",
    ):
        trigger.widget_created(widget, data, mode)

    @classmethod
    def connect_internal_signals(cls):
        pass

    @classmethod
    def connect_widget_signals(cls, widget: ui.RelationshipWidget):
        w = widget
        widget.closed.connect(lambda: trigger.widget_closed(w))
        widget.cb_fraction.toggled.connect(
            lambda: w.ds_fraction.setEnabled(w.cb_fraction.isChecked())
        )

    @classmethod
    def is_related_class_valid(
        cls, value, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary
    ):
        if dict_utils.is_uri(value):
            return True
        if isinstance(widget.data, BsddClass):
            element = cl_utils.get_class_by_code(bsdd_dictionary, value)
        elif isinstance(widget.data, BsddProperty):
            element = prop_utils.get_property_by_code(value, bsdd_dictionary)
        if element is None:
            return False
        if element == widget.data:
            return False
        return True
