from bsdd_gui.presets.ui_presets import FieldWidget
from . import trigger
from .qt.ui_Widget import Ui_Form


class GopWidget(FieldWidget, Ui_Form):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.widget_created(self)
