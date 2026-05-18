from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication
from bsdd_gui.module.loin import constants
from bsdd_gui.module.iso_export import constants as iso_constants
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.loin import ui,models,model_views
    from bsdd_json import BsddClass

import qtawesome as qta

def connect_signals(loin: Type[tool.Loin],class_view:type[tool.PPClassView],property_view:type[tool.PPPropertyView]):
    loin.connect_internal_signals()
    class_view.connect_internal_signals()
    property_view.connect_internal_signals()

def retranslate_ui(loin: Type[tool.Loin]):
    pass


def register_widget(widget: ui.Widget, loin: Type[tool.Loin],project:type[tool.Project]):
    loin.register_widget(widget)
    model: models.ClassTreeModel = widget.tv_classes.model()
    model.beginResetModel()
    model.bsdd_data = project.get()
    model.endResetModel()
    widget.pb_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
    widget.pb_export.setIcon(qta.icon("mdi6.tray-arrow-down"))

def connect_widget(widget: ui.Widget, loin: Type[tool.Loin],class_view:type[tool.PPClassView],property_view:type[tool.PPPropertyView]):
    loin.connect_widget_signals(widget)
    class_view.connect_view_signals(widget.tv_classes)
    property_view.connect_view_signals(widget.tv_properties)
    widget.pb_import.clicked.connect(lambda _=False, w=widget: loin.request_xml_import(w))
    widget.pb_export.clicked.connect(lambda _=False, w=widget: loin.request_xml_export(w))

def register_class_view(view: model_views.ClassView, class_view: type[tool.PPClassView]):
    class_view.register_view(view)
    from bsdd_gui.module.loin.uc_ms import ClassModel
    view.setModel(ClassModel())

def register_property_view(
    view: model_views.PropertyView, property_view: type[tool.PPPropertyView]
):
    property_view.register_view(view)
    from bsdd_gui.module.loin.uc_ms import PropertyModel
    view.setModel(PropertyModel())


def register_pset_view(view: model_views.PsetView):
    from bsdd_gui.module.loin.uc_ms import PsetModel
    view.setModel(PsetModel())



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
        property_tree_view = class_view.get_property_view(class_tree_view)
        proxy_model: models.SortModel = property_tree_view.model()
        model = proxy_model
        model.beginResetModel()
        model.bsdd_data = data
        model.endResetModel()

    class_view.signals.selection_changed.connect(update_property_view)
    property_view.connect_view_signals(view)


def create_widget(args,loin:type[tool.Loin]):
    loin.create_widget(*args)




def export_to_xml(widget:ui.Widget,loin: Type["tool.Loin"],appdata:Type[tool.Appdata],popups:Type[tool.Popups]) -> int:
    """Write the current LOIN to *out_path* (ISO 7817-3 XML). Returns spec count."""
    text = QCoreApplication.translate("IDSExport", "Export IDS settings")
    old_path = appdata.get_path(constants.APPDATA_OPTION)
    new_path = popups.get_save_path(iso_constants.LOIN_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.APPDATA_OPTION, new_path)
    
    return loin.export_to_xml(new_path)


def import_from_xml(widget:ui.Widget,loin: Type["tool.Loin"],project:Type[tool.Project],appdata:Type[tool.Appdata],popups:Type[tool.Popups]) -> None:
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
    loin._adopt_loin(new_loin,project.get())

def reset(loin:type[tool.Loin]):
    loin.reset()


def apply_checkstate_to_children(
    bsdd_class: "BsddClass",
    purpose_guid,
    milestone_guid,
    loin: Type[tool.Loin],
) -> None:
    loin.apply_checkstate_to_children(bsdd_class, purpose_guid, milestone_guid)


def remove_class(
    bsdd_class: "BsddClass",
    loin: Type[tool.Loin],
) -> None:
    loin.remove_class(bsdd_class)


def add_classes_from_drop(
    codes: list[str],
    loin: Type[tool.Loin],
    project: Type[tool.Project],
) -> None:
    loin.add_classes(codes, project.get())