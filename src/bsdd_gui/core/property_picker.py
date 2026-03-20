from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QModelIndex

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_picker import ui,models,model_views
    from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM
    from bsdd_json import BsddClass


def connect_signals(property_picker: Type[tool.PropertyPicker],class_tree:type[tool.IdsClassView],property_tree:type[tool.IdsPropertyView]):
    property_picker.connect_internal_signals()
    class_tree.connect_internal_signals()
    property_tree.connect_internal_signals()

def retranslate_ui(property_picker: Type[tool.PropertyPicker]):
    pass


def register_widget(widget: ui.Widget, property_picker: Type[tool.PropertyPicker],project:type[tool.Project],class_tree:type[tool.IdsClassView],property_tree:type[tool.IdsPropertyView]):
    property_picker.register_widget(widget)
    model: models.ClassTreeModel = widget.tv_classes.model().sourceModel()
    model.beginResetModel()
    model.bsdd_data = project.get()
    model.endResetModel()

def connect_widget(widget: ui.Widget, property_picker: Type[tool.PropertyPicker],class_tree:type[tool.IdsClassView],property_tree:type[tool.IdsPropertyView]):
    property_picker.connect_widget_signals(widget)
    class_view = widget.tv_classes
    property_view = widget.tv_properties
    class_tree.connect_view_signals(class_view)
    property_tree.connect_view_signals(property_view)


def register_class_view(view: model_views.ClassView, ids_class_view: type[tool.IdsClassView]):
    ids_class_view.register_view(view)


def register_property_view(
    view: model_views.PropertyView, ids_property_view: type[tool.IdsPropertyView]
):
    ids_property_view.register_view(view)


def add_columns_to_class_view(
    view: model_views.ClassView, ids_class: type[tool.IdsClassView], project: type[tool.Project]
):
    def set_checkstate(model: CTM, index: QModelIndex, value: bool):
        bsdd_class = index.internalPointer()
        ids_class.set_checkstate(bsdd_class, value)

    data = project.get()
    proxy_model, model = ids_class.create_model(data)
    ids_class.add_column_to_table(model, "Name", lambda a: a.Name)
    ids_class.add_column_to_table(model, "Code", lambda a: a.Code)
    ids_class.add_column_to_table(model, "Export", ids_class.get_checkstate, set_checkstate)
    view.setModel(proxy_model)


def add_columns_to_property_view(
    view: model_views.PropertyView,
    ids_property: type[tool.IdsPropertyView],
    project: type[tool.Project],
):

    data = project.get()
    proxy_model, model = ids_property.create_model(data)

    def set_checkstate(model: CTM, index: QModelIndex, value: bool):
        bsdd_property = index.internalPointer()
        ids_property.set_checkstate(model, model.bsdd_data, bsdd_property, value)

    ids_property.add_column_to_table(model, "Name", ids_property._get_name)
    ids_property.add_column_to_table(model, "Code", ids_property._get_code)
    ids_property.add_column_to_table(
        model, "Export", lambda cp: ids_property.get_checkstate(model, cp), set_checkstate
    )

    view.setModel(proxy_model)


def connect_class_view(view: model_views.ClassView, ids_class: type[tool.IdsClassView]):
    ids_class.connect_view_signals(view)


def connect_property_view(
    view: model_views.PropertyView,
    ids_property: type[tool.IdsPropertyView],
    ids_class: type[tool.IdsClassView],
):

    def update_property_view(
        class_view: model_views.ClassView,
        data: BsddClass,
    ):
        widget: ui.Widget = class_view.window()
        property_view = widget.tv_properties
        proxy_model: models.SortModel = property_view.model()
        model = proxy_model.sourceModel()
        model.beginResetModel()
        model.bsdd_data = data
        model.endResetModel()

    ids_class.signals.selection_changed.connect(update_property_view)
    ids_property.connect_view_signals(view)