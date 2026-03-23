from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_picker as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui, model_views


def connect():
    core.connect_signals(tool.PropertyPicker, tool.IdsClassView, tool.IdsPropertyView)


def retranslate_ui():
    core.retranslate_ui(tool.PropertyPicker)


def on_new_project():
    pass


def create_widget(*args, **kwargs):
    core.create_widget(args, tool.PropertyPicker)


def widget_created(widget: ui.Widget):
    core.register_widget(
        widget,
        tool.PropertyPicker,
        tool.Project,
        tool.IdsClassView,
        tool.IdsPropertyView,
    )
    core.connect_widget(widget, tool.PropertyPicker, tool.IdsClassView, tool.IdsPropertyView)


def class_view_created(view: model_views.ClassView):
    core.register_class_view(view, tool.IdsClassView)
    core.add_columns_to_class_view(view, tool.IdsClassView, tool.Project)
    core.connect_class_view(view, tool.IdsClassView)


def property_view_created(view: model_views.PropertyView):
    core.register_property_view(view, tool.IdsPropertyView)
    core.add_columns_to_property_view(view, tool.IdsPropertyView, tool.Project)
    core.connect_property_view(view, tool.IdsPropertyView, tool.IdsClassView)
