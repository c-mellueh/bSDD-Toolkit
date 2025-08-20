import logging
import os
import argparse


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def create_module(name: str):
    module_path = os.path.abspath(os.path.join(os.curdir, "module", name))

    if os.path.exists(module_path):
        logging.warning("Module already exists")
    else:
        os.mkdir(module_path)
    init_path = os.path.join(module_path, "__init__.py")
    if os.path.exists(init_path):
        logging.warning("__init__.py already exists")
    with open(init_path, "w") as f:
        f.write(
            f"""import som_gui
from . import ui, prop, trigger


def register():
    som_gui.{to_camel_case(name)}Properties = prop.{to_camel_case(name)}Properties()

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

class {to_camel_case(name)}Properties:
    pass

"""
        )
    trigger_path = os.path.join(module_path, "trigger.py")
    if os.path.exists(trigger_path):
        logging.warning("trigger.py already exists")
    with open(trigger_path, "w") as f:
        f.write(
            f"""from __future__ import annotations
import som_gui
from som_gui import tool
from som_gui.core import {name} as core
from typing import TYPE_CHECKING


def connect():
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
            f"""

    """
        )


def create_core(name: str):
    core_path = os.path.abspath(os.path.join(os.curdir, "core", f"{name}.py"))
    if os.path.exists(core_path):
        logging.warning("core.py already exists")
    with open(core_path, "w") as f:
        f.write(
            f"""from __future__ import annotations

from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from som_gui import tool
"""
        )


def create_tool(name: str):
    tool_path = os.path.abspath(os.path.join(os.curdir, "tool", f"{name}.py"))
    if os.path.exists(tool_path):
        logging.warning("tool.py already exists")
    with open(tool_path, "w") as f:
        f.write(
            f"""
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import som_gui.core.tool
import som_gui

if TYPE_CHECKING:
    from som_gui.module.{name}.prop import {to_camel_case(name)}Properties


class {to_camel_case(name)}(som_gui.core.tool.{to_camel_case(name)}):
    @classmethod
    def get_properties(cls) -> {to_camel_case(name)}Properties:
        return som_gui.{to_camel_case(name)}Properties
"""
        )


def update_tools():
    file_path = "core/tool.py"
    from som_gui import _update_tools

    with open(file_path, "w") as f:
        _update_tools.main(f)


def main(name: str):
    create_core(name)
    create_tool(name)
    create_module(name)
    update_tools()


# Create the parser
parser = argparse.ArgumentParser(
    description="Script to run a module with a name argument"
)

# Add the "name" argument
parser.add_argument("name", type=str, help="Name of the module to run")

# Parse the arguments
args = parser.parse_args()
if __name__ == "__main__":
    main(args.name)
    # you need to add module to tool.__init__.py by hand
