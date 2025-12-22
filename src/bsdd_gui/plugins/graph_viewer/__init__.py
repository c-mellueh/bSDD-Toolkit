import logging

# name and description will be used for Settings Window
friendly_name = "Graph Viewer"
description = "UI for displaying Node Relations"
author = "christoph.mellueh.de"


def activate():
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("graph_viewer")
    logging.info("Activate Graph Viewer")

    for name, module in submodules:
        module.register()
    for name, module in submodules:
        module.activate()


def deactivate():
    logging.info("Deactivate Graph Viewer")
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("graph_viewer")
    for name, module in submodules:
        module.deactivate()


def on_new_project():
    logging.info("New Project Graph Viewer")
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("graph_viewer")
    for _, module in submodules:
        module.on_new_project()


def retranslate_ui():
    logging.info("Retranslate Graph Viewer")
    from bsdd_gui import tool

    submodules = tool.Plugins.get_submodules("graph_viewer")
    for name, module in submodules:
        module.retranslate_ui()


if __name__ == "__main__":
    pass
