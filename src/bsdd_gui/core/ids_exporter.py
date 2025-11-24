from __future__ import annotations
from PySide6.QtCore import QCoreApplication, QModelIndex
from typing import TYPE_CHECKING, Type
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui.module.ids_exporter import constants
import json
import os
import ifctester
from ifctester.facet import Property as PropertyFacet
from ifctester.facet import Entity as EntityFacet
from ifctester.facet import Restriction
from ifctester.ids import Specification
from bsdd_gui.presets.ui_presets import run_iterable_with_progress

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.ids_exporter import ui, model_views, models
    from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
    from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM


def connect_to_main_window(
    ids_exporter: Type[tool.IdsExporter],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action(
        None, "Ids Exporter", lambda: ids_exporter.request_dialog(project.get(), main_window.get())
    )
    ids_exporter.set_action(main_window.get(), "open_window", action)


def retranslate_ui(ids_exporter: Type[tool.IdsExporter], main_window: Type[tool.MainWindowWidget]):
    action = ids_exporter.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("IDSExport", "Graph View"))


def connect_signals(
    widget_tool: Type[tool.IdsExporter],
    ids_class: Type[tool.IdsClassView],
    ids_property: Type[tool.IdsPropertyView],
):
    widget_tool.connect_internal_signals()
    ids_class.connect_internal_signals()
    ids_property.connect_internal_signals()


def create_widget(data: BsddDictionary, parent, widget_tool: Type[tool.IdsExporter]):
    widget: ui.IdsWidget = widget_tool.show_widget(data, parent)


def create_dialog(data: BsddDictionary, parent, dialog_tool: Type[tool.IdsExporter]):
    dialog = dialog_tool.create_dialog(data, parent)
    text = QCoreApplication.translate("IdsExport", "IDS Exporter")
    dialog.setWindowTitle(text)
    widget = dialog_tool.get_widget()
    model: models.ClassTreeModel = widget.tv_classes.model().sourceModel()
    model.beginResetModel()
    model.bsdd_data = data
    model.endResetModel()
    geom = dialog.geometry()
    dialog.setGeometry(geom.x(), geom.y(), 1075, 710)
    if dialog.exec():
        dialog_tool.sync_to_model(dialog._widget, data)
        dialog_tool.signals.dialog_accepted.emit(dialog)
    else:
        dialog_tool.signals.dialog_declined.emit(dialog)


def register_widget(widget: ui.IdsWidget, widget_tool: Type[tool.IdsExporter]):
    widget_tool.register_widget(widget)
    if not widget.fw_template.get_path():
        widget.fw_template.set_path(widget_tool.get_template())


def register_fields(widget: ui.IdsWidget, widget_Tool: Type[tool.IdsExporter]):
    pass
    # widget_Tool.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget, widget_tool: Type[tool.IdsExporter], util: Type[tool.Util]):
    pass


def connect_widget(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    ids_class: Type[tool.IdsClassView],
    main_window: Type[tool.MainWindowWidget],
):
    worker, thread, dialog = widget_tool.count_properties_with_progress(
        main_window.get(), widget.bsdd_data.Classes
    )
    widget._count_worker = worker
    widget._count_thread = thread
    widget._count_dialog = dialog
    worker.finished.connect(lambda: widget_tool.fill_pset_combobox(widget))
    widget_tool.connect_widget_signals(widget)
    class_view = widget.tv_classes
    ids_class.connect_settings_signals(widget, class_view)


def register_class_view(view: model_views.ClassView, ids_class_view: Type[tool.IdsClassView]):
    ids_class_view.register_view(view)


def register_property_view(
    view: model_views.PropertyView, ids_property_view: Type[tool.IdsPropertyView]
):
    ids_property_view.register_view(view)


def add_columns_to_class_view(
    view: model_views.ClassView,
    ids_class: Type[tool.IdsClassView],
    ids_exporter: Type[tool.IdsExporter],
):
    def set_checkstate(model: CTM, index: QModelIndex, value: bool):
        bsdd_class = index.internalPointer()
        ids_class.set_checkstate(bsdd_class, value)

    data = ids_exporter.get_data()
    proxy_model, model = ids_class.create_model(data)
    ids_class.add_column_to_table(model, "Name", lambda a: a.Name)
    ids_class.add_column_to_table(model, "Code", lambda a: a.Code)
    ids_class.add_column_to_table(model, "Export", ids_class.get_checkstate, set_checkstate)
    view.setModel(proxy_model)


def add_columns_to_property_view(
    view: model_views.PropertyView,
    ids_property: Type[tool.IdsPropertyView],
    ids_exporter: Type[tool.IdsExporter],
):

    data = ids_exporter.get_data()
    proxy_model, model = ids_property.create_model(data)

    def set_checkstate(model: CTM, index: QModelIndex, value: bool):
        bsdd_class = index.internalPointer()
        ids_property.set_checkstate(model, bsdd_class, value)

    ids_property.add_column_to_table(model, "Name", ids_property._get_name)
    ids_property.add_column_to_table(model, "Code", ids_property._get_code)
    ids_property.add_column_to_table(
        model, "Export", lambda cp: ids_property.get_checkstate(model, cp), set_checkstate
    )

    view.setModel(proxy_model)


def connect_class_view(view: model_views.ClassView, ids_class: Type[tool.IdsClassView]):
    ids_class.connect_view_signals(view)


def connect_property_view(
    view: model_views.PropertyView,
    ids_property: Type[tool.IdsPropertyView],
    ids_class: Type[tool.IdsClassView],
):

    def update_property_view(
        class_view: model_views.ClassView,
        data: BsddClass,
    ):
        dialog: ui.IdsDialog = class_view.window()
        property_view = dialog._widget.tv_properties
        proxy_model: models.SortModel = property_view.model()
        model = proxy_model.sourceModel()
        model.beginResetModel()
        model.bsdd_data = data
        model.endResetModel()

    ids_class.signals.selection_changed.connect(update_property_view)
    ids_property.connect_view_signals(view)


def export_settings(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    class_view: Type[tool.IdsClassView],
    property_view: Type[tool.IdsPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    class_dict = class_view.get_check_dict()
    property_dict = property_view.get_check_dict()
    settings_dict = widget_tool.get_settings(widget)
    full_dict = {
        "class_settings": class_dict,
        "property_settings": property_dict,
        "settings": settings_dict,
    }
    text = QCoreApplication.translate("IDSExport", "Export IDS settings")
    old_path = appdata.get_path(constants.IDS_APPDATA)
    new_path = popups.get_save_path(constants.FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.IDS_APPDATA, new_path)
    with open(new_path, "w") as file:
        json.dump(full_dict, file)


def import_settings(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    class_view: Type[tool.IdsClassView],
    property_view: Type[tool.IdsPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    old_path = appdata.get_path(constants.IDS_APPDATA)
    text = QCoreApplication.translate("IDSExport", "Import IDS settings")
    new_path = popups.get_open_path(constants.FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.IDS_APPDATA, new_path)
    with open(new_path, "r") as file:
        full_dict = json.load(file)
    class_dict = full_dict.get("class_settings", {})
    property_dict = full_dict.get("property_settings", {})
    settings_dict = full_dict.get("settings", {})
    class_view.set_check_dict(class_dict, widget.tv_classes)
    property_view.set_check_dict(property_dict, widget.tv_properties)
    widget_tool.set_settings(widget, settings_dict)
    pass


def export_ids(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    class_view: Type[tool.IdsClassView],
    property_view: Type[tool.IdsPropertyView],
):
    class_settings = class_view.get_check_dict()
    property_settings = property_view.get_check_dict()
    main_settings = widget_tool.get_settings(widget)
    out_path = widget.fw_output.get_path()
    template_path = widget.fw_template.get_path()
    data_type = "IfcLabel"  # IfcLabel or IfcText
    ifc_versions = [
        "IFC4X3_ADD2",
    ]

    bsdd_dict = widget.bsdd_data
    ids = ifctester.ids.open(template_path)
    base_spec = ids.specifications[0]
    base_requirement: PropertyFacet = base_spec.requirements[0]
    base_requirement.propertySet = main_settings.get("main_pset", "")
    base_requirement.baseName = main_settings.get("main_property", "")
    base_restriction = base_requirement.value
    base_restriction.options = {"enumeration": [c.Code for c in bsdd_dict.Classes]}

    # If Inherit is Checked it will build the class settings dict exclude subclasses of unchecked classes
    if main_settings["inherit"]:
        class_settings = widget_tool.build_inherited_checkstate_dict(
            bsdd_dict.Classes, class_settings
        )

    for bsdd_class in sorted(bsdd_dict.Classes, key=lambda x: x.Code):
        if not class_settings.get(bsdd_class.Code, True):
            continue

        spec = Specification(
            f"Check for {bsdd_class.Code}",
            ifcVersion=ifc_versions,
            identifier=bsdd_class.Code,
            description="Auto-generated from bSDD",
        )
        applicability_facet = PropertyFacet(
            base_requirement.propertySet,
            base_requirement.baseName,
            bsdd_class.Code,
            data_type,
            cardinality="optional",
        )
        spec.applicability.append(applicability_facet)
        for class_prop in bsdd_class.ClassProperties:
            if widget_tool.is_class_prop_active(class_prop, property_settings):
                spec.requirements += widget_tool.build_property_requirements(class_prop, bsdd_dict)
        spec.requirements += widget_tool.build_ifc_requirements(bsdd_class, bsdd_dict)
        ids.specifications.append(spec)
    ids.to_xml(out_path)
