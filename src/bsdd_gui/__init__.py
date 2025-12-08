from __future__ import annotations

__version__ = "0.2.5.1"  # needs to be on top of bsdd_gui import statements else ImportError

import logging
from typing import TYPE_CHECKING
import bsdd_gui
from bsdd_gui import core, tool
from bsdd_gui.resources.icons import get_icon
import importlib
import pkgutil

if TYPE_CHECKING:
    from bsdd_gui.module.main_window_widget.ui import MainWindow
    from types import ModuleType


# list all modules which are defined in the modules folder
module = importlib.import_module("bsdd_gui.module")
# define Modules which should be initialized before the other Modules
preregister = ["main_window_widget"]

# Import Modules
modules: list[tuple[str, ModuleType]] = list()
for m in pkgutil.iter_modules(module.__path__):
    if not m.ispkg:
        continue
    logging.info(f"Importing Module '{m.name}'")
    path = f"bsdd_gui.module.{m.name}"
    modules.append((m.name, importlib.import_module(path)))


def register():
    """
    registers the Properties of each Module
    :return:
    """
    # call the register() function in the __init__.py of every Module
    # Start with the Preregister
    for module_name in preregister:
        index = [x[0] for x in modules].index(module_name)
        modules[index][1].register()

    for name, module in modules:
        if name not in preregister:
            module.register()


def load_ui_triggers():
    """
    registers the PySide6 Signals/Slots of the Ui
    :return:
    """
    # call the load_ui_trigger() in the __init__.py of every Module
    # Start with the Preregister
    for module_name in preregister:
        index = [x[0] for x in modules].index(module_name)
        modules[index][1].load_ui_triggers()

    for name, module in modules:
        if name not in preregister:
            module.load_ui_triggers()


def retranslate_ui():
    """
    retranslates the UI to the set Language
    :return:
    """
    # call the retranslate_ui() in the __init__.py of every Module
    for name, module in modules:
        module.retranslate_ui()


def on_new_project():
    # call the on_new_project() in the __init__.py of every Module

    for name, module in modules:
        module.on_new_project()
