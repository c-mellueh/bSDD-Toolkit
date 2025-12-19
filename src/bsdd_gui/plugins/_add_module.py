import logging
import os
import argparse


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def create_module(plugin_name: str, module_name: str, abbrev: str, prop_name: str):
    module_path = os.path.abspath(os.path.join(os.curdir, plugin_name, "module", module_name))
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

    
def activate():
    trigger.activate()

    
def deactivate():
    trigger.deactivate()

    
def retranslate_ui():
    trigger.retranslate_ui()

    
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

class {prop_name}:
    pass

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
from bsdd_gui.plugins.{plugin_name}.core import {module_name} as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.{plugin_name} import tool as {abbrev}_tool
if TYPE_CHECKING:
    from . import ui


def activate():
    pass

    
def deactivate():
    pass

    
def retranslate_ui():
    pass

    
def on_new_project():
    pass
"""
        )
    ui_path = os.path.join(module_path, "ui.py")
    if os.path.exists(ui_path):
        logging.warning("ui.py already exists")
    with open(ui_path, "w") as f:
        f.write(
            f"""from __future__ import annotations
from typing import TYPE_CHECKING
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets import BaseWidget

    """
        )


def create_core(plugin_name: str, module_name: str, abbrev: str):
    core_path = os.path.abspath(os.path.join(os.curdir, plugin_name, "core", f"{module_name}.py"))
    if os.path.exists(core_path):
        logging.warning("core.py already exists")

    with open(core_path, "w") as f:
        f.write(
            f"""from __future__ import annotations

from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.{plugin_name} import tool as {abbrev}_tool
    from bsdd_gui.plugins.{plugin_name}.module.{module_name} import ui
"""
        )


def create_tool(plugin_name: str, module_name: str, prop_name: str):
    tool_path = os.path.abspath(os.path.join(os.curdir, plugin_name, "tool", f"{module_name}.py"))

    if os.path.exists(tool_path):
        logging.warning("tool.py already exists")
    with open(tool_path, "w") as f:
        f.write(
            f"""
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.{plugin_name}.module.{module_name} import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.{plugin_name}.module.{module_name}.prop import {prop_name}

class Signals():
    pass

class {to_camel_case(module_name)}:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> {prop_name}:
        return bsdd_gui.{prop_name}

    @classmethod
    def _get_trigger(cls):
        return trigger
"""
        )


def main(plugin_name: str, module_name: str, abbreviation: str):
    curdir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(curdir)
    prop_name = f"{to_camel_case(f"{plugin_name}_{module_name}")}Properties"

    create_core(plugin_name, module_name, abbreviation)
    create_tool(plugin_name, module_name, prop_name)
    create_module(plugin_name, module_name, abbreviation, prop_name)


# Create the parser
parser = argparse.ArgumentParser(description="Script to run a module with a name argument")

# Add the "name" argument
parser.add_argument("name", type=str, help="Name of the module to run")
parser.add_argument("plugin_name", type=str, help="Name of the Plugin")
parser.add_argument("abbreviation", type=str, help="Abbreviation of Plugin")


# Parse the arguments
args = parser.parse_args()
if __name__ == "__main__":
    # print(os.path.abspath(__file__))
    main(args.plugin_name, args.name, args.abbreviation)
    # you need to add module to tool.__init__.py by hand
