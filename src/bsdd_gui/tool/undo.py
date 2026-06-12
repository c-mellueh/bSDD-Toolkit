from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QAction

import bsdd_gui
from bsdd_json import BsddDictionary

if TYPE_CHECKING:
    from bsdd_gui.module.undo.prop import UndoProperties

MAX_STACK_SIZE = 50
DEBOUNCE_MS = 400


class Signals(QObject):
    stacks_changed = Signal()


class Undo:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> UndoProperties:
        return bsdd_gui.UndoProperties

    @classmethod
    def serialize(cls, bsdd_dictionary: BsddDictionary) -> str:
        return json.dumps(bsdd_dictionary.model_dump(mode="json", exclude_none=True))

    @classmethod
    def deserialize(cls, state: str) -> BsddDictionary:
        return BsddDictionary.model_validate(json.loads(state))

    @classmethod
    def reset(cls, state: str | None) -> None:
        """Forget all history and make *state* the new baseline."""
        props = cls.get_properties()
        props.undo_stack.clear()
        props.redo_stack.clear()
        props.last_state = state
        if props.debounce_timer is not None:
            props.debounce_timer.stop()
        cls.signals.stacks_changed.emit()

    @classmethod
    def schedule_checkpoint(cls) -> None:
        """(Re)start the debounce timer; rapid edits collapse into one step."""
        if cls.is_restoring():
            return
        cls._get_timer().start(DEBOUNCE_MS)

    @classmethod
    def checkpoint_if_changed(cls, current_state: str) -> bool:
        """Push the previous state onto the undo stack if *current_state* differs."""
        props = cls.get_properties()
        if props.last_state is None:
            props.last_state = current_state
            return False
        if current_state == props.last_state:
            return False
        props.undo_stack.append(props.last_state)
        if len(props.undo_stack) > MAX_STACK_SIZE:
            props.undo_stack.pop(0)
        props.redo_stack.clear()
        props.last_state = current_state
        logging.debug(f"Undo checkpoint ({len(props.undo_stack)} steps)")
        cls.signals.stacks_changed.emit()
        return True

    @classmethod
    def can_undo(cls) -> bool:
        return bool(cls.get_properties().undo_stack)

    @classmethod
    def can_redo(cls) -> bool:
        return bool(cls.get_properties().redo_stack)

    @classmethod
    def pop_undo(cls, current_state: str) -> str:
        props = cls.get_properties()
        props.redo_stack.append(current_state)
        state = props.undo_stack.pop()
        props.last_state = state
        cls.signals.stacks_changed.emit()
        return state

    @classmethod
    def pop_redo(cls, current_state: str) -> str:
        props = cls.get_properties()
        props.undo_stack.append(current_state)
        state = props.redo_stack.pop()
        props.last_state = state
        cls.signals.stacks_changed.emit()
        return state

    @classmethod
    def is_restoring(cls) -> bool:
        return cls.get_properties().is_restoring

    @classmethod
    def set_restoring(cls, value: bool) -> None:
        cls.get_properties().is_restoring = value

    @classmethod
    def set_action(cls, name: str, action: QAction) -> None:
        cls.get_properties().actions[name] = action

    @classmethod
    def get_action(cls, name: str) -> QAction | None:
        return cls.get_properties().actions.get(name)

    @classmethod
    def _get_timer(cls) -> QTimer:
        props = cls.get_properties()
        if props.debounce_timer is None:
            from bsdd_gui.module.undo import trigger

            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(trigger.debounce_elapsed)
            props.debounce_timer = timer
        return props.debounce_timer
