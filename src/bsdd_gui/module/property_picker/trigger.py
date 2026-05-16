from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_picker as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui, model_views


def connect():
    core.connect_signals(tool.PropertyPicker, tool.PPClassView, tool.PPPropertyView)


def retranslate_ui():
    core.retranslate_ui(tool.PropertyPicker)


def on_new_project():
    core.reset(tool.PropertyPicker)

    pass


def create_widget(*args, **kwargs):
    core.create_widget(args, tool.PropertyPicker)


def widget_created(widget: ui.Widget):
    core.register_widget(
        widget,
        tool.PropertyPicker,
        tool.Project
    )
    core.connect_widget(widget, tool.PropertyPicker, tool.PPClassView, tool.PPPropertyView)


def class_view_created(view: model_views.ClassView):
    core.register_class_view(view, tool.PPClassView)
    core.connect_class_view(view, tool.PPClassView)


def property_view_created(view: model_views.PropertyView):
    core.register_property_view(view, tool.PPPropertyView)
    core.connect_property_view(view, tool.PPPropertyView, tool.PPClassView)


def context_menu_requested(*_):
    pass


def classes_dropped(codes: list[str]) -> None:
    core.add_classes_from_drop(codes, tool.PropertyPicker, tool.Project)


def class_removed(bsdd_class) -> None:
    core.remove_class(bsdd_class, tool.PropertyPicker)


def apply_checkstate_to_children(bsdd_class, purpose_guid, milestone_guid) -> None:
    core.apply_checkstate_to_children(bsdd_class, purpose_guid, milestone_guid, tool.PropertyPicker)

def import_xml(widget: ui.Widget) -> None:
    core.import_from_xml(widget, tool.PropertyPicker, tool.Project, tool.Appdata, tool.Popups)

def export_xml(widget: ui.Widget) -> None:
    core.export_to_xml(widget,tool.PropertyPicker, tool.Appdata, tool.Popups)