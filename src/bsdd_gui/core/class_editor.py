from __future__ import annotations
from PySide6.QtCore import QModelIndex
from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClass
import logging

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_editor import ui


def register_widget(widget: ui.ClassEditor, class_editor: Type[tool.ClassEditor]):
    class_editor.register_widget(widget)


def connect_signals(class_editor: Type[tool.ClassEditor]):
    class_editor.connect_signaller()


def connect_to_main_window(
    class_editor: Type[tool.ClassEditor], main_window: Type[tool.MainWindow]
):
    def emit_class_info_requested(index: QModelIndex):
        index = view.model().mapToSource(index)
        bsdd_class = index.internalPointer()
        if not bsdd_class:
            return
        class_editor.signaller.class_info_requested.emit(bsdd_class)

    view = main_window.get_class_view()
    view.doubleClicked.connect(emit_class_info_requested)


def open_class_editor(bsdd_class: BsddClass, class_editor: Type[tool.ClassEditor]):
    logging.warning(f"Open Class Editor for {bsdd_class.Code}")
    widget = class_editor.create_widget(bsdd_class)
    widget.show()
    print(widget)
