from bsdd_gui.module.class_tree_view.ui import ClassView
from . import trigger


class GroupOfPropertiesView(ClassView):
    def get_trigger(self):
        return trigger

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


