from __future__ import annotations

from PySide6.QtCore import QObject

from bsdd_gui import tool
from bsdd_gui.core import inheritance as core
from bsdd_gui.module.undo.trigger import MUTATION_SIGNAL_NAMES


def connect():
    core.create_main_menu_actions(tool.Inheritance, tool.MainWindowWidget)
    # every edit of the model is checked against the inheritance rules
    connected = set()
    for attribute in vars(tool).values():
        signals = getattr(attribute, "signals", None)
        if not isinstance(signals, QObject) or signals in connected:
            continue
        connected.add(signals)
        for name in MUTATION_SIGNAL_NAMES:
            signal = getattr(signals, name, None)
            if signal is not None:
                signal.connect(data_changed)


def data_changed(*_args):
    core.changed(tool.Inheritance, tool.Project, tool.Undo)


def check_requested():
    core.check(
        tool.Inheritance,
        tool.Project,
        tool.Undo,
        tool.Popups,
        tool.MainWindowWidget,
        tool.ClassTreeView,
        tool.PropertySetTableView,
        tool.ClassPropertyTableView,
    )


def dialog_requested():
    core.open_dialog(tool.Inheritance, tool.Project, tool.MainWindowWidget)


def strict_toggled(checked: bool):
    core.set_strict(
        checked,
        tool.Inheritance,
        tool.Project,
        tool.Popups,
        tool.MainWindowWidget,
        tool.PropertySetTableView,
        tool.ClassPropertyTableView,
    )


def on_new_project():
    core.project_changed(tool.Inheritance, tool.Project, tool.Undo)


def retranslate_ui():
    core.retranslate_ui(tool.Inheritance)
