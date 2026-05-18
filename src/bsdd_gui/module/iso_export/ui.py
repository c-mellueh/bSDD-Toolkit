from bsdd_gui.presets.ui_presets import FieldWidget
from bsdd_json import BsddDictionary
from .qt.ui_Widget import Ui_Form
from . import trigger


class Widget(FieldWidget, Ui_Form):
    def __init__(self, data: BsddDictionary, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.bsdd_data: BsddDictionary
        self.setupUi(self)

        trigger.widget_created(self)
