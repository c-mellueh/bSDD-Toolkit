from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_picker import ui,models,model_views
    from bsdd_json import BsddClass



def connect_signals(property_picker: Type[tool.PropertyPicker],class_view:type[tool.PPClassView],property_view:type[tool.PPPropertyView]):
    property_picker.connect_internal_signals()
    class_view.connect_internal_signals()
    property_view.connect_internal_signals()

def retranslate_ui(property_picker: Type[tool.PropertyPicker]):
    pass


def register_widget(widget: ui.Widget, property_picker: Type[tool.PropertyPicker],project:type[tool.Project]):
    property_picker.register_widget(widget)
    model: models.ClassTreeModel = widget.tv_classes.model()
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
    #data = project.get()
    #proxy_model, _ = class_view.create_model(data)
    from bsdd_gui.module.property_picker.uc_ms import UcMsColumnProxy
    
    view.setModel(UcMsColumnProxy())


def add_columns_to_property_view(
    view: model_views.PropertyView,
    property_view: type[tool.PPPropertyView],
    project: type[tool.Project],
):
    # data = project.get()
    # proxy_model, model = property_view.create_model(data)
    from bsdd_gui.module.property_picker.uc_ms import UcMsColumnProxy
    
    view.setModel(UcMsColumnProxy())


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
        model = proxy_model
        model.beginResetModel()
        model.bsdd_data = data
        model.endResetModel()

    class_view.signals.selection_changed.connect(update_property_view)
    property_view.connect_view_signals(view)


def create_widget(args,property_picker:type[tool.PropertyPicker]):
    property_picker.create_widget(*args)




def export_to_xml(property_picker: Type["tool.PropertyPicker"], out_path: str) -> int:
    """Write the current LOIN to *out_path* (ISO 7817-3 XML). Returns spec count."""
    return property_picker.export_to_xml(out_path)


def import_from_xml(in_path: str,property_picker: Type["tool.PropertyPicker"],project:Type[tool.Project]) -> None:
    """Replace the current LOIN with the contents of *in_path*."""
    with open(in_path, "rb") as f:
        xml_bytes = f.read()
    from bsdd_gui.module.iso_export.datamodel import LoinLevelOfInformationNeed

    new_loin = LoinLevelOfInformationNeed.from_xml(xml_bytes)
    property_picker._adopt_loin(new_loin,project.get())

def reset(property_picker:type[tool.PropertyPicker]):
    property_picker.reset()