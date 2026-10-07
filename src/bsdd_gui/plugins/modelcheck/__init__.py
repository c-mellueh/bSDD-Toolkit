import logging

friendly_name = "Modelcheck"
description = "Validate IFC models against bSDD Dictionaries"
author = "bSDD-Toolkit"


def activate():
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("modelcheck")
    logging.info("Activate Modelcheck")
    for name, module in submodules:
        if hasattr(module, "register"):
            module.register()
    for name, module in submodules:
        if hasattr(module, "activate"):
            module.activate()


def deactivate():
    logging.info("Deactivate Modelcheck")
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("modelcheck")
    for name, module in submodules:
        if hasattr(module, "deactivate"):
            module.deactivate()


def on_new_project():
    logging.info("New Project Modelcheck")
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("modelcheck")
    for _, module in submodules:
        if hasattr(module, "on_new_project"):
            module.on_new_project()


def retranslate_ui():
    logging.info("Retranslate Modelcheck")
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("modelcheck")
    for name, module in submodules:
        if hasattr(module, "retranslate_ui"):
            module.retranslate_ui()
