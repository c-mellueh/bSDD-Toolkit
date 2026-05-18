from __future__ import annotations


from bsdd_gui.resources.icons import get_icon
from . import trigger
from .qt.ui_Widget import Ui_Form
from bsdd_gui.presets.ui_presets import FieldWidget


class PropertyWidget(FieldWidget, Ui_Form):

    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.setWindowIcon(get_icon())
        self.setupUi(self)
        trigger.widget_created(self)
