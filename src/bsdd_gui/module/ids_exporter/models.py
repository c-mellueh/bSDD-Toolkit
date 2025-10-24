from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM
from bsdd_gui.module.class_tree_view.models import SortModel as SM
from bsdd_gui import tool


class ClassTreeModel(CTM):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data, tool.IdsClassView, *args, **kwargs)


class SortModel(SM):
    pass
