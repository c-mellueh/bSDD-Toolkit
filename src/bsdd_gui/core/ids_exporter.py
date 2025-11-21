from __future__ import annotations
from PySide6.QtCore import QCoreApplication, QModelIndex
from typing import TYPE_CHECKING, Type
from bsdd_json.utils import property_utils as prop_utils

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
    action.setText(QCoreApplication.translate("GraphView", "Graph View"))


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
    text = QCoreApplication.translate("Preset", "Example Title")
    dialog.setWindowTitle(text)
    widget = dialog_tool.get_widget()
    model: models.ClassTreeModel = widget.tv_classes.model().sourceModel()
    model.beginResetModel()
    model.bsdd_data = data
    model.endResetModel()
    if dialog.exec():
        dialog_tool.sync_to_model(dialog._widget, data)
        dialog_tool.signals.dialog_accepted.emit(dialog)
    else:
        dialog_tool.signals.dialog_declined.emit(dialog)


def register_widget(widget: ui.IdsWidget, widget_tool: Type[tool.IdsExporter]):
    widget_tool.register_widget(widget)


def register_fields(widget: ui.IdsWidget, widget_Tool: Type[tool.IdsExporter]):
    pass
    # widget_Tool.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget, widget_tool: Type[tool.IdsExporter], util: Type[tool.Util]):
    pass


def connect_widget(
    widget: ui.IdsWidget, widget_tool: Type[tool.IdsExporter], ids_class: Type[tool.IdsClassView]
):
    widget_tool.count_properties(widget.bsdd_data)
    widget_tool.connect_widget_signals(widget)
    class_view = widget.tv_classes
    ids_class.connect_settings_signals(widget, class_view)
    widget_tool.fill_pset_combobox(widget)


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
        class_view: model_views.ClassView, data: BsddClass,
    ):
        dialog:ui.IdsDialog = class_view.window()
        property_view = dialog._widget.tv_properties
        proxy_model: models.SortModel = property_view.model()
        model = proxy_model.sourceModel()
        model.beginResetModel()
        model.bsdd_data = data
        model.endResetModel()

    ids_class.signals.selection_changed.connect(update_property_view)
    ids_property.connect_view_signals(view)
