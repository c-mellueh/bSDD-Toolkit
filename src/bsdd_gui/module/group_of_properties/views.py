from bsdd_gui.module.class_tree_view.ui import ClassView
from bsdd_gui.module.class_property_table_view.ui import ClassPropertyTable

from . import trigger


class GopClassView(ClassView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_created(self):
        self.get_trigger().class_view_created(self)

    def get_trigger(self):
        return trigger


class GopPropertyView(ClassPropertyTable):
    def get_trigger(self):
        return trigger

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_created(self):
        self.get_trigger().property_view_created(self)

    def get_trigger(self):
        return trigger
