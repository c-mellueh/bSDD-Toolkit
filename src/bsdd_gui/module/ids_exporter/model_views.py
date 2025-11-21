from PySide6.QtWidgets import QTreeView
from . import trigger


class ClassView(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.class_view_created(self)


class PropertyView(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.property_view_created(self)
