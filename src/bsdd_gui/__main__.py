from __future__ import annotations
import sys
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QApplication

import som_gui.plugins

if TYPE_CHECKING:
    from os import PathLike

from som_gui import core, tool
import som_gui.core.main_window
import som_gui.core.project
from som_gui.module.project.constants import OPEN_PATH
from som_gui.module.language.trigger import set_language
import importlib


def main(initial_file: PathLike | None = None, log_level=None, open_last_project=False):
    """
    Opens the Application and starts the GUI
    :param initial_file: SOMJson file that will be opened on startup
    :param log_level: Logging level that will be set on startup
    :param open_last_project: Should the last project be opened?
    :return:
    """
    print("START")

    if log_level is not None:
        tool.Logging.set_log_level(log_level)

    som_gui.register()

    # Create UI
    app = QApplication(sys.argv)
    som_gui.core.main_window.create_main_window(app, tool.MainWindow, tool.PropertySet)
    som_gui.load_ui_triggers()
    for plugin_names in tool.Plugins.get_available_plugins():
        if tool.Plugins.is_plugin_active(plugin_names):
            module = importlib.import_module(f"som_gui.plugins.{plugin_names}")
            module.activate()

    som_gui.core.project.create_project(tool.Project)

    if initial_file is not None:
        som_gui.core.project.open_project(initial_file, tool.Project, tool.Plugins)

    elif open_last_project:
        som_gui.core.project.open_project(
            tool.Appdata.get_path(OPEN_PATH), tool.Project, tool.Plugins
        )

    set_language(None)
    sys.exit(app.exec())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="sample argument parser")
    parser.add_argument(
        "open_path", help="Path to Project", default=None, type=str, nargs="?"
    )
    parser.add_argument(
        "-l", "--log-level", help="Logging level", default=None, type=int
    )
    parser.add_argument(
        "-ol",
        "--open_last_project",
        help="Open last project",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()
    main(args.open_path, args.log_level, args.open_last_project)
