from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QModelIndex

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_picker import ui,models,model_views
    from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM
    from bsdd_json import BsddClass


def connect_signals(property_picker: Type[tool.PropertyPicker],class_view:type[tool.PPClassView],property_view:type[tool.PPPropertyView]):
    property_picker.connect_internal_signals()
    class_view.connect_internal_signals()
    property_view.connect_internal_signals()

def retranslate_ui(property_picker: Type[tool.PropertyPicker]):
    pass


def register_widget(widget: ui.Widget, property_picker: Type[tool.PropertyPicker],project:type[tool.Project]):
    property_picker.register_widget(widget)
    model: models.ClassTreeModel = widget.tv_classes.model().sourceModel()
    model.beginResetModel()
    model.bsdd_data = project.get()
    model.endResetModel()

def connect_widget(widget: ui.Widget, property_picker: Type[tool.PropertyPicker],class_view:type[tool.PPClassView],property_view:type[tool.PPPropertyView]):
    property_picker.connect_widget_signals(widget)
    class_view.connect_view_signals(widget.tv_classes)
    property_view.connect_view_signals(widget.tv_properties)


def register_class_view(view: model_views.ClassView, class_view: type[tool.PPClassView]):
    class_view.register_view(view)


def register_property_view(
    view: model_views.PropertyView, property_view: type[tool.PPPropertyView]
):
    property_view.register_view(view)


def add_columns_to_class_view(
    view: model_views.ClassView, class_view: type[tool.PPClassView], project: type[tool.Project]
):
    def set_checkstate(model: CTM, index: QModelIndex, value: bool):
        bsdd_class = index.internalPointer()
        class_view.set_checkstate(bsdd_class, value,view)

    data = project.get()
    proxy_model, model = class_view.create_model(data)
    class_view.add_column_to_table(model, "Name", lambda a: a.Name)
    class_view.add_column_to_table(model, "Code", lambda a: a.Code)
    class_view.add_column_to_table(model, "Export", lambda c,v=view:class_view.get_checkstate(c,v), set_checkstate)
    view.setModel(proxy_model)


def add_columns_to_property_view(
    view: model_views.PropertyView,
    property_view: type[tool.PPPropertyView],
    project: type[tool.Project],
):

    data = project.get()
    proxy_model, model = property_view.create_model(data)

    def set_checkstate(model: CTM, index: QModelIndex, value: bool,v:model_views.PropertyView):
        bsdd_property = index.internalPointer()
        property_view.set_checkstate(v,  bsdd_property, value)

    property_view.add_column_to_table(model, "Name", property_view._get_name)
    property_view.add_column_to_table(model, "Code", property_view._get_code)
    property_view.add_column_to_table(
        model, "Export", lambda cp,v=view: property_view.get_checkstate(v, cp),lambda *args,v=view: set_checkstate(*args,v)
    )

    view.setModel(proxy_model)


def connect_class_view(tree_view: model_views.ClassView, class_view: type[tool.PPClassView]):
    class_view.connect_view_signals(tree_view)


def connect_property_view(
    view: model_views.PropertyView,
    property_view: type[tool.PPPropertyView],
    class_view: type[tool.PPClassView],
):

    def update_property_view(
        class_tree_view: model_views.ClassView,
        data: BsddClass,
    ):
        property_tree_ivew = class_view.get_property_view(class_tree_view)
        proxy_model: models.SortModel = property_tree_ivew.model()
        model = proxy_model.sourceModel()
        model.beginResetModel()
        model.bsdd_data = data
        model.endResetModel()

    class_view.signals.selection_changed.connect(update_property_view)
    property_view.connect_view_signals(view)


def create_widget(args,property_picker:type[tool.PropertyPicker]):
    property_picker.create_widget(*args)