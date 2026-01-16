from __future__ import annotations

from typing import TYPE_CHECKING
from PySide6.QtCore import Qt, Signal, QModelIndex
from . import trigger
from bsdd_json import BsddClassProperty, BsddProperty
from bsdd_gui.presets.ui_presets import TableItemView
from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit

if TYPE_CHECKING:
    from . import models


class AllowedValuesTable(TableItemView):
    editor_closed = Signal(QLineEdit, object)

    def __init__(self, *args, bsdd_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: BsddClassProperty | BsddProperty = bsdd_data
        self.horizontalHeader().setStretchLastSection(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        trigger.view_created(self)

    def model(self) -> models.SortModel:
        return super().model()

    def closeEditor(self, editor, hint):
        self.editor_closed.emit(editor, hint)
        return super().closeEditor(editor, hint)


class LiveEditDelegate(QStyledItemDelegate):

    text_edited = Signal(QModelIndex, str, str)
    text_set = Signal(QModelIndex, str)

    def createEditor(self, parent, option, index):
        source_index = self.parent().model().mapToSource(index)
        bsdd_value = source_index.internalPointer()
        editor = QLineEdit(parent)
        editor._old_text = index.data(Qt.ItemDataRole.EditRole)
        editor._bsdd_value = bsdd_value
        editor.textEdited.connect(
            lambda new_text, i=index, e=editor: self.one_text_edit(i, e, new_text)
        )
        return editor

    def setModelData(self, editor, model, index):
        source_index = self.parent().model().mapToSource(index)
        self.text_set.emit(source_index, editor.text())

    def one_text_edit(self, index: QModelIndex, editor: QLineEdit, new_text: str):
        source_index = self.parent().model().mapToSource(index)
        self.text_edited.emit(source_index, editor._old_text, new_text)
        editor._old_text = new_text
