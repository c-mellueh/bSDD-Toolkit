from bsdd_gui.presets.ui_presets import BaseWidget
from . import trigger

class GopWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.widget_created(self)

    