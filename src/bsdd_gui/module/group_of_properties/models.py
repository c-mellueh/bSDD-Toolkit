from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM
from bsdd_gui.module.class_tree_view.models import SortModel as CSM
from bsdd_gui.module.class_property_table_view.models import ClassPropertyTableModel as PTM
from bsdd_gui.module.class_property_table_view.models import SortModel as PSM

from bsdd_json import BsddClass
from bsdd_json.utils import class_utils as cl_utils


class ClassTreeModel(CTM):
    def __init__(self, tl=None, bsdd_data=None, *args, **kwargs):
        from bsdd_gui.tool import GopClassView

        super().__init__(GopClassView, bsdd_data, *args, **kwargs)

    def _get_root_classes(self):
        rc = cl_utils.get_root_classes(self.bsdd_dictionary)
        return [c for c in rc if c.ClassType == "GroupOfProperties"]

    def _get_children(self, bsdd_class: BsddClass):
        children = cl_utils.get_children(bsdd_class)
        return [c for c in children if c.ClassType == "GroupOfProperties"]


class ClassSortModel(CSM):
    pass


class PropertyTableModel(PTM):
    def __init__(self, tl=None, bsdd_data=None, *args, **kwargs):
        from bsdd_gui.tool import GopPropertyView

        super().__init__(GopPropertyView, bsdd_data, *args, **kwargs)

    @property
    def active_class(self):
        from bsdd_gui.tool import GroupOfProperties

        return GroupOfProperties.get_active_class()

    @property
    def active_pset(self):
        from bsdd_gui.tool import GroupOfProperties

        active_class = GroupOfProperties.get_active_class()
        return active_class.Name


class PropertySortModel(PSM):
    pass
