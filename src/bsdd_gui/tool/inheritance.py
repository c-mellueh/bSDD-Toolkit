from __future__ import annotations

import json
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction

import bsdd_gui
from bsdd_json import BsddDictionary
from bsdd_json.utils import inheritance_utils as iu

if TYPE_CHECKING:
    from bsdd_gui.module.inheritance.prop import InheritanceProperties
    from bsdd_gui.module.inheritance.ui import ProjectSettingsDialog

SETTING = "strict_inheritance"


class Inheritance:
    """Strict inheritance: every child class has all class properties of its parent class.
    The rules are in :mod:`bsdd_json.utils.inheritance_utils`."""

    @classmethod
    def get_properties(cls) -> InheritanceProperties:
        return bsdd_gui.InheritanceProperties

    @classmethod
    def serialize(cls, bsdd_dictionary: BsddDictionary) -> str:
        return json.dumps(bsdd_dictionary.model_dump(mode="json", exclude_none=True))

    @classmethod
    def remember(cls, bsdd_dictionary: BsddDictionary | None) -> None:
        """Make the current state the reference for the next check."""
        props = cls.get_properties()
        if bsdd_dictionary is None:
            props.snapshot = None
            props.last_good = None
            return
        props.snapshot = iu.snapshot(bsdd_dictionary)
        props.last_good = cls.serialize(bsdd_dictionary)

    @classmethod
    def get_last_good(cls) -> str | None:
        return cls.get_properties().last_good

    @classmethod
    def is_unchanged(cls, bsdd_dictionary: BsddDictionary) -> bool:
        return cls.serialize(bsdd_dictionary) == cls.get_properties().last_good

    @classmethod
    def apply(cls, bsdd_dictionary: BsddDictionary) -> list[str]:
        """Pass parent changes on to the children and add missing inherited data.

        Returns the rule violations; nothing is completed if there are any (the caller restores
        the last good state)."""
        before = cls.get_properties().snapshot
        if before is not None:
            errors = iu.propagate_and_guard(bsdd_dictionary, before, raise_errors=False)
            if errors:
                return errors
        iu.complete(bsdd_dictionary)
        cls.remember(bsdd_dictionary)
        return []

    @classmethod
    def complete(cls, bsdd_dictionary: BsddDictionary) -> int:
        added = iu.complete(bsdd_dictionary)
        cls.remember(bsdd_dictionary)
        return added

    @classmethod
    def missing_count(cls, bsdd_dictionary: BsddDictionary) -> int:
        return iu.missing_count(bsdd_dictionary)

    @classmethod
    def schedule_check(cls) -> None:
        """Check after the current event has been handled (an edit may emit several signals)."""
        props = cls.get_properties()
        if props.timer is None:
            from bsdd_gui.module.inheritance import trigger

            props.timer = QTimer()
            props.timer.setSingleShot(True)
            props.timer.timeout.connect(trigger.check_requested)
        props.timer.start(0)

    @classmethod
    def set_action(cls, action: QAction) -> None:
        cls.get_properties().action = action

    @classmethod
    def get_action(cls) -> QAction | None:
        return cls.get_properties().action

    @classmethod
    def create_dialog(cls, parent) -> ProjectSettingsDialog:
        from bsdd_gui.module.inheritance import trigger, ui

        dialog = ui.ProjectSettingsDialog(parent)
        dialog.toggle_strict.toggled.connect(trigger.strict_toggled)
        cls.get_properties().dialog = dialog
        return dialog

    @classmethod
    def get_dialog(cls) -> ProjectSettingsDialog | None:
        return cls.get_properties().dialog

    @classmethod
    def set_dialog(cls, dialog: ProjectSettingsDialog | None) -> None:
        cls.get_properties().dialog = dialog

    @classmethod
    def set_toggle_checked(cls, checked: bool) -> None:
        dialog = cls.get_dialog()
        if dialog is None:
            return
        dialog.toggle_strict.blockSignals(True)
        dialog.toggle_strict.setChecked(checked)
        dialog.toggle_strict.blockSignals(False)
