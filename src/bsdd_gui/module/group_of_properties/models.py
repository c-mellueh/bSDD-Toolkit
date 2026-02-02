from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM
from bsdd_gui.module.class_tree_view.models import SortModel as SM
from bsdd_json import BsddClass
from bsdd_json.utils import class_utils as cl_utils


class ClassTreeModel(CTM):
    def __init__(self, bsdd_dictionary, tl=None, *args, **kwargs):
        from bsdd_gui.tool import GopClassView

        super().__init__(bsdd_dictionary, GopClassView, *args, **kwargs)

    def _get_root_classes(self):
        rc = cl_utils.get_root_classes(self.bsdd_dictionary)
        return [c for c in rc if c.ClassType == "GroupOfProperties"]

    def _get_children(self, bsdd_class: BsddClass):
        children = cl_utils.get_children(bsdd_class)
        return [c for c in children if c.ClassType == "GroupOfProperties"]


class SortModel(SM):
    pass
