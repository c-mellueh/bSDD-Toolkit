from PySide6.QtWidgets import QTreeView
from . import trigger
from bsdd_gui.presets.ui_presets import TagInput


class ClassView(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.class_view_created(self)


class PropertyView(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.property_view_created(self)


class TagInput_IfcVersion(TagInput):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, allowed=["IFC2X3", "IFC4", "IFC4X3_ADD2"], minimum_le_width=100, **kwargs
        )
