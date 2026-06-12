from __future__ import annotations

import logging

from PySide6.QtCore import QObject

from bsdd_gui import tool
from bsdd_gui.core import undo as core

# Signal names (on any tool's `signals` object) that indicate the bSDD model
# was mutated. Anything missed here is still caught by the flush that runs
# right before every undo/redo.
MUTATION_SIGNAL_NAMES = (
    "data_changed",
    "class_added",
    "class_removed",
    "class_parent_changed",
    "class_property_added",
    "class_property_removed",
    "property_added",
    "property_removed",
    "class_relation_added",
    "class_relation_removed",
    "property_relation_added",
    "property_relation_removed",
    "ifc_relation_addded",
    "ifc_relation_removed",
    "related_ifc_added",
    "related_ifc_removed",
    "property_set_added",
    "property_set_deleted",
    "field_changed",
    "value_changed",
    "item_added",
    "item_removed",
    "code_changed",
    "property_reference_changed",
)


def connect():
    core.create_main_menu_actions(tool.Undo, tool.MainWindowWidget)
    tool.Undo.signals.stacks_changed.connect(stacks_changed)
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
                logging.debug(f"Undo tracks {type(signals).__module__}.{name}")


def data_changed(*_args):
    core.changed(tool.Undo, tool.Project)


def debounce_elapsed():
    core.flush(tool.Undo, tool.Project)


def undo_requested():
    core.perform_undo(tool.Undo, tool.Project, tool.MainWindowWidget)


def redo_requested():
    core.perform_redo(tool.Undo, tool.Project, tool.MainWindowWidget)


def stacks_changed():
    core.update_action_states(tool.Undo)


def on_new_project():
    core.project_changed(tool.Undo, tool.Project)


def retranslate_ui():
    core.retranslate_ui(tool.Undo)
