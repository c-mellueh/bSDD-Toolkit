from bsdd_gui.module.class_tree_view.ui import ClassView
from bsdd_gui.module.class_property_table_view.ui import ClassPropertyTable

from . import trigger


class GopClassView(ClassView):
    def get_trigger(self):
        return trigger

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GopPropertyView(ClassPropertyTable):
    def get_trigger(self):
        return trigger

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)