from __future__ import annotations
from typing import TYPE_CHECKING
import ctypes

from PySide6.QtCore import QObject, Signal
import bsdd_gui

from bsdd_gui.module.class_tree import ui, models, trigger

if TYPE_CHECKING:
    from bsdd_gui.module.class_tree.prop import ClassTreeProperties
    from bsdd_parser.models import BsddDictionary, BsddClass


class Signaller(QObject):
    model_refresh_requested = Signal()


class ClassTree:
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassTreeProperties:
        return bsdd_gui.ClassTreeProperties

    @classmethod
    def connect_signals(cls):
        cls.signaller.model_refresh_requested.connect(trigger.reset_class_views)

    @classmethod
    def register_class_view(cls, class_view: ui.ClassView):
        cls.get_properties().class_views.add(class_view)

    @classmethod
    def unregister_class_view(cls, class_view: ui.ClassView):
        cls.get_properties().class_views.pop(class_view)

    @classmethod
    def create_model(cls,bsdd_dictionary:BsddDictionary):
        model = models.ClassTreeModel(bsdd_dictionary)
        return model

    @classmethod
    def get_root_classes(cls, bsdd_dictionary: BsddDictionary):
        return [c for c in bsdd_dictionary.Classes if not c.ParentClassCode]

    @classmethod
    def get_children(cls, bsdd_class: BsddClass):
        code = bsdd_class.Code
        bsdd_dictionary = bsdd_class._parent_ref()
        return [c for c in bsdd_dictionary.Classes if c.ParentClassCode == code]

    @classmethod
    def get_tree_views(cls) -> set[ui.ClassView]:
        return cls.get_properties().class_views

    @classmethod
    def get_class_by_code(cls, bsdd_dictionary: BsddDictionary, code: str):
        return {c.Code: c for c in bsdd_dictionary.Classes}.get(code)

    @classmethod
    def get_row_index(cls, bsdd_class: BsddClass):
        bsdd_dictionary = bsdd_class._parent_ref()
        if not bsdd_class.ParentClassCode:
            return bsdd_dictionary.Classes.index(bsdd_class)
        parent_class = cls.get_class_by_code(bsdd_dictionary, bsdd_class.ParentClassCode)
        return cls.get_children(parent_class).index(bsdd_class)