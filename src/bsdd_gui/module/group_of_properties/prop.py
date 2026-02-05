from __future__ import annotations
from bsdd_gui.presets.prop_presets import  FieldProperties, ActionsProperties
from ..class_tree_view.prop import ClassTreeViewProperties
from ..class_property_table_view.prop import ClassPropertyTableViewProperties


class GroupOfPropertiesProperties(ActionsProperties, FieldProperties):
    def __init__(self):
        super().__init__()
        self.active_class = None
        self.active_class_property = None

class GopClassViewProperties(ClassTreeViewProperties):
    def __init__(self):
        super().__init__()


class GopPropertyViewProperties(ClassPropertyTableViewProperties):
    def __init__(self):
        super().__init__()
