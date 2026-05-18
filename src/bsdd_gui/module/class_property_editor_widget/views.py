from __future__ import annotations


from PySide6.QtWidgets import QWidget, QGridLayout
from bsdd_gui.presets.ui_presets.label_tags_input import TagInput
from . import trigger
from .qt.ui_SplitterSettings import Ui_SplitterSettings


class ValueView(QGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ValueTagInput(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)


class SplitterSettings(QWidget, Ui_SplitterSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.splitter_settings_created(self)
