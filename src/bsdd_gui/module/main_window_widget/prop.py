from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu
import bsdd_json
from bsdd_gui.presets.prop_presets import ActionsProperties

if TYPE_CHECKING:
    from bsdd_gui.module.main_window_widget.ui import MainWindow
    from bsdd_gui.module.main_window_widget.qt.ui_MainWindow import Ui_MainWindow
    from bsdd_json.models import BsddClass, BsddClassProperty


class MainWindowWidgetProperties(ActionsProperties):
    ui: Ui_MainWindow | None = None
    window: MainWindow = None
    application: QApplication = None
    active_class: BsddClass = None
    active_pset: str = None
    active_property: BsddClassProperty = None

    # Most Modules have an Actions dict. In this dict The Actions of the MainMenubar are stored. and can be called by get/set action w/ their name
    # This is Mostly used for translating the Actions on Language change
