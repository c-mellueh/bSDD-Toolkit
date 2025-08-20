from __future__ import annotations
from PySide6.QtWidgets import QApplication
from typing import Type,TYPE_CHECKING
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree import ui


def connect_signals(class_tree: Type[tool.ClassTree]):
    class_tree.connect_signals()


def connect_class_view(class_view:ui.ClassView,class_tree:Type[tool.ClassTree],project: Type[tool.Project]):
    class_tree.register_class_view(class_view)
    bsdd_dictionary = project.get()
    model = class_tree.create_model(bsdd_dictionary)
    class_view.setModel(model)


def reset_class_views(class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    bsdd_dictionary = project.get()
    for tree_view in class_tree.get_tree_views():
        model = class_tree.create_model(bsdd_dictionary)
        tree_view.setModel(model)
