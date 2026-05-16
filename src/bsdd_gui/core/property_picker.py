from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication
from bsdd_gui.module.property_picker import constants
from bsdd_gui.module.iso_export import constants as iso_constants
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
    from bsdd_gui.module.property_picker.uc_ms import ClassModel
    
    view.setModel(ClassModel())


def add_columns_to_property_view(
    view: model_views.PropertyView,
    property_view: type[tool.PPPropertyView],
    project: type[tool.Project],
):
    # data = project.get()
    # proxy_model, model = property_view.create_model(data)
    from bsdd_gui.module.property_picker.uc_ms import ClassModel
    
    view.setModel(ClassModel())


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




def export_to_xml(widget:ui.Widget,property_picker: Type["tool.PropertyPicker"],appdata:Type[tool.Appdata],popups:Type[tool.Popups]) -> int:
    """Write the current LOIN to *out_path* (ISO 7817-3 XML). Returns spec count."""
    text = QCoreApplication.translate("IDSExport", "Export IDS settings")
    old_path = appdata.get_path(constants.APPDATA_OPTION)
    new_path = popups.get_save_path(iso_constants.LOIN_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.APPDATA_OPTION, new_path)
    
    return property_picker.export_to_xml(new_path)


def import_from_xml(widget:ui.Widget,property_picker: Type["tool.PropertyPicker"],project:Type[tool.Project],appdata:Type[tool.Appdata],popups:Type[tool.Popups]) -> None:
    """Replace the current LOIN with the contents of *in_path*."""
    
    text = QCoreApplication.translate("IDSExport", "Export IDS settings")
    old_path = appdata.get_path(constants.APPDATA_OPTION)
    new_path = popups.get_open_path(iso_constants.LOIN_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.APPDATA_OPTION, new_path)
    
    with open(new_path, "rb") as f:
        xml_bytes = f.read()
    from bsdd_gui.module.iso_export.datamodel import LoinLevelOfInformationNeed

    new_loin = LoinLevelOfInformationNeed.from_xml(xml_bytes)
    property_picker._adopt_loin(new_loin,project.get())

def reset(property_picker:type[tool.PropertyPicker]):
    property_picker.reset()


def apply_checkstate_to_children(
    bsdd_class: "BsddClass",
    purpose_guid,
    milestone_guid,
    property_picker: Type[tool.PropertyPicker],
) -> None:
    property_picker.apply_checkstate_to_children(bsdd_class, purpose_guid, milestone_guid)


def remove_class(
    bsdd_class: "BsddClass",
    property_picker: Type[tool.PropertyPicker],
) -> None:
    property_picker.remove_class(bsdd_class)


def add_classes_from_drop(
    codes: list[str],
    property_picker: Type[tool.PropertyPicker],
    project: Type[tool.Project],
) -> None:
    property_picker.add_classes(codes, project.get())