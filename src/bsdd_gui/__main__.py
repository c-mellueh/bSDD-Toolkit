from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

# xdg-desktop-portal is the Linux/Wayland portal integration. On Windows the
# platform-theme plugin doesn't exist; forcing it causes Qt to crash with a
# native access violation when the main window is shown.
if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORMTHEME", "xdgdesktopportal")

if TYPE_CHECKING:
    from os import PathLike

from bsdd_gui import core, tool
import bsdd_gui.core.main_window_widget
import importlib
from bsdd_gui.module.project.constants import OPEN_PATH
import bsdd_gui.core.project
import bsdd_gui.core.main_window_widget
from bsdd_gui.module.language.trigger import set_language
from bsdd_gui.module.ifc_helper.data import IfcHelperData


def _apply_system_color_scheme(app: QApplication) -> None:
    if app.styleHints().colorScheme() != Qt.ColorScheme.Dark:
        return
    app.setStyle("Fusion")
    palette = QPalette()
    dark = QColor(53, 53, 53)
    darker = QColor(35, 35, 35)
    text = Qt.GlobalColor.white
    disabled = QColor(127, 127, 127)
    highlight = QColor(42, 130, 218)
    palette.setColor(QPalette.ColorRole.Window, dark)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, darker)
    palette.setColor(QPalette.ColorRole.AlternateBase, dark)
    palette.setColor(QPalette.ColorRole.ToolTipBase, darker)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, dark)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, highlight)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, disabled)
    app.setPalette(palette)


def main(
    initial_file: PathLike | None = None,
    log_level=None,
    open_last_project=False,
    offline_mode=False,
):
    """
    Opens the Application and starts the GUI
    :param initial_file: SOMJson file that will be opened on startup
    :param log_level: Logging level that will be set on startup
    :param open_last_project: Should the last project be opened?
    :return:
    """
    print("START")
    if not offline_mode:
        IfcHelperData.get_classes()

    if log_level is not None:
        tool.Logging.set_log_level(log_level)

    bsdd_gui.register()
    tool.Project.set_offline_mode(offline_mode)

    # Create UI
    app = QApplication(sys.argv)
    _apply_system_color_scheme(app)
    bsdd_gui.core.main_window_widget.create_main_window(app, tool.MainWindowWidget)
    bsdd_gui.load_ui_triggers()

    for plugin_names in tool.Plugins.get_available_plugins():
        if tool.Plugins.is_plugin_active(plugin_names):
            module = importlib.import_module(f"bsdd_gui.plugins.{plugin_names}")
            module.activate()

    bsdd_gui.core.project.create_project(tool.Project)

    if initial_file is not None:
        bsdd_gui.core.project.open_project(
            initial_file, tool.Project, tool.Popups, tool.FileLock, appdata=tool.Appdata
        )

    elif open_last_project:
        pass
        bsdd_gui.core.project.open_project(
            tool.Appdata.get_path(OPEN_PATH),
            tool.Project,
            tool.Popups,
            tool.FileLock,
            appdata=tool.Appdata,
        )

    set_language(None)
    if tool.AiHelper.is_active():
        tool.AiHelper.load_client()
    sys.exit(app.exec())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="sample argument parser")
    parser.add_argument("open_path", help="Path to Project", default=None, type=str, nargs="?")
    parser.add_argument("-l", "--log-level", help="Logging level", default=None, type=int)
    parser.add_argument(
        "-ol", "--open_last_project", help="Open last project", default=False, action="store_true"
    )
    parser.add_argument(
        "-ofm", "--offline_mode", help="Offline Mode", default=False, action="store_true"
    )
    args = parser.parse_args()
    main(args.open_path, args.log_level, args.open_last_project, args.offline_mode)
