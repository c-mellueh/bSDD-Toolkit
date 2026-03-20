import logging
import os
import argparse


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def create_module(name: str):
    module_path = os.path.abspath(os.path.join(os.curdir, "module", name))
    tool_name = to_camel_case(name)
    prop_name = f"{to_camel_case(name)}Properties"
    widget_name = "Widget"
    if os.path.exists(module_path):
        logging.warning("Module already exists")
    else:
        os.mkdir(module_path)
    init_path = os.path.join(module_path, "__init__.py")
    if os.path.exists(init_path):
        logging.warning("__init__.py already exists")
    with open(init_path, "w") as f:
        f.write(
            f"""import bsdd_gui
from . import ui, prop, trigger


def register():
    bsdd_gui.{prop_name} = prop.{prop_name}()

def retranslate_ui():
    trigger.retranslate_ui()

def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()

"""
        )

    prop_path = os.path.join(module_path, "prop.py")
    if os.path.exists(prop_path):
        logging.warning("prop.py already exists")
    with open(prop_path, "w") as f:
        f.write(
            f"""from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties,WidgetProperties

class {prop_name}(ActionsProperties,WidgetProperties):
    def __init__(self):
        super().__init__()

"""
        )
    trigger_path = os.path.join(module_path, "trigger.py")
    if os.path.exists(trigger_path):
        logging.warning("trigger.py already exists")
    with open(trigger_path, "w") as f:
        f.write(
            f"""from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import {name} as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.{tool_name})


def retranslate_ui():
    core.retranslate_ui(tool.{tool_name})

def on_new_project():
    pass
    
def create_widget(data: object, parent: ui.{widget_name}):
    core.create_widget(data, parent, tool.{tool_name})


#def create_dialog(data: object, parent: ui.{widget_name}):
#    core.create_dialog(data, parent, tool.{tool_name})


def widget_created(widget: ui{widget_name}):
    core.register_widget(widget, tool.{tool_name})
    core.register_fields(widget, tool.{tool_name})
    core.register_validators(widget, tool.{tool_name}, tool.Util)
    core.connect_widget(widget, tool.{tool_name})
    
"""
        )
    ui_path = os.path.join(module_path, "ui.py")
    if os.path.exists(ui_path):
        logging.warning("ui.py already exists")
    with open(ui_path, "w") as f:
        f.write(
            f"""
from bsdd_gui.presets.ui_presets import BaseDialog, ui.{widget_name}, BaseWindow
from bsdd_json import  BsddDictionary
from .qt.ui_Widget import Ui_Form
from . import trigger

class {widget_name}(ui.{widget_name},Ui_Form):
    def __init__(self, data: BsddDictionary, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.bsdd_data: BsddDictionary
        self.setupUi(self)

        trigger.widget_created(self)
    """
        )


def create_core(name: str):
    tool_name = to_camel_case(name)
    widget_name = "Widget"
    core_path = os.path.abspath(os.path.join(os.curdir, "core", f"{name}.py"))
    if os.path.exists(core_path):
        logging.warning("core.py already exists")
    with open(core_path, "w") as f:
        f.write(
f"""from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClassProperty, BsddProperty
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.{name} import ui


def connect_signals({name}: Type[tool.{tool_name}]):
    {name}.connect_internal_signals()


def retranslate_ui({name}: Type[{tool_name}]):
    pass


def create_widget(data, parent, {name}: Type[{tool_name}]):
    {name}.show_widget(data, parent)


def create_dialog(data: object, parent, {name}: Type[tool.{tool_name}]):
    dialog = {name}.create_dialog(data, parent)
    text = QCoreApplication.translate("Preset", "Example Title")
    dialog.setWindowTitle(text)
    if dialog.exec():
        {name}.sync_to_model(dialog._widget, data)
        {name}.signals.dialog_accepted.emit(dialog)
    else:
        {name}.signals.dialog_declined.emit(dialog)


def register_widget(widget: ui.{widget_name}, {name}: Type[{tool_name}]):
    {name}.register_widget(widget)


def register_fields(widget: ui.{widget_name}, {name}: Type[{tool_name}]):
    {name}.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget:ui.{widget_name}, {name}: Type[{tool_name}], util: Type[tool.Util]):
    {name}.add_validator(
        widget,
        widget.le_code,
        lambda v, w,: {name}.is_code_valid(v, w),
        lambda w, v: util.set_invalid(w, not v),
    )


def connect_widget(widget: ui.{widget_name}, {name}: Type[{tool_name}]):
    {name}.connect_widget_signals(widget)

"""
        )


def create_tool(name: str):
    tool_path = os.path.abspath(os.path.join(os.curdir, "tool", f"{name}.py"))
    tool_name = to_camel_case(name)
    prop_name = f"{to_camel_case(name)}Properties"
    widget_name = "Widget"

    if os.path.exists(tool_path):
        logging.warning("tool.py already exists")
    with open(tool_path, "w") as f:
        f.write(
            f"""
from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal

import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool,WidgetTool,WidgetSignals
from bsdd_gui.module.{name} import ui

if TYPE_CHECKING:
    from bsdd_gui.module.{name}.prop import {prop_name}

clas Signals(WidgetSignals):
    pass

class {tool_name}:
    @classmethod
    def get_properties(cls) -> {prop_name}:
        return bsdd_gui.{prop_name}

    @classmethod
    def _get_widget_class(cls) -> Type[ui.{widget_name}]:
        return ui.{widget_name}

    @classmethod
    def create_widget(cls, *args, **kwargs) -> ui.{widget_name}:
        widget = cls._get_widget_class()(*args, **kwargs)
        cls.add_plugins_to_widget(widget)
        return widget

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.{widget_name}):
        super().connect_widget_signals(widget)
    
"""
        )


def main(name: str):
    os.chdir("bsdd_gui")
    create_core(name)
    create_tool(name)
    create_module(name)


# Create the parser
parser = argparse.ArgumentParser(description="Script to run a module with a name argument")

# Add the "name" argument
parser.add_argument("name", type=str, help="Name of the module to run")

# Parse the arguments
args = parser.parse_args()
if __name__ == "__main__":
    main(args.name)
    # you need to add module to tool.__init__.py by hand
