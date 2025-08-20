from __future__ import annotations
from PySide6.QtWidgets import QApplication
from typing import Type,TYPE_CHECKING
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree import ui

def connect_class_view(class_view:ui.ClassView,class_tree:Type[tool.ClassTree],project: Type[tool.Project]):
    bsdd_dictionary = project.get()
    model = class_tree.create_model(bsdd_dictionary)
    class_view.setModel(model)