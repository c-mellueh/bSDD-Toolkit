from __future__ import annotations
from typing import TYPE_CHECKING
import ctypes

from PySide6.QtWidgets import QApplication
import bsdd_gui

from bsdd_gui.module.class_tree import ui,models
if TYPE_CHECKING:
    from bsdd_gui.module.class_tree.prop import ClassTreeProperties
    from bsdd_parser.models import BsddDictionary

class ClassTree:
    @classmethod
    def get_properties(cls) -> ClassTreeProperties:
        return bsdd_gui.ClassTreeProperties
    
    @classmethod
    def create_model(cls,bsdd_dictionary:BsddDictionary):
        model = models.ClassTreeModel(bsdd_dictionary)
        return model