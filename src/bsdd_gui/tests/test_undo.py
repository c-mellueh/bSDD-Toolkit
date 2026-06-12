"""
Tests for snapshot-based undo/redo (tool/undo.py + core/undo.py).

The project dictionary is swapped to a small test instance per test;
bsdd_gui.on_new_project is stubbed out so restores don't rebuild real views.
"""

from __future__ import annotations

import pytest
from bsdd_json import BsddClass

import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import undo as core_undo
from bsdd_gui.tool.undo import MAX_STACK_SIZE, Undo


@pytest.fixture()
def project(dictionary, monkeypatch, qapp):
    """Install *dictionary* as the active project and reset undo state."""
    props = tool.Project.get_properties()
    old_dictionary = props.project_dictionary
    props.project_dictionary = dictionary
    monkeypatch.setattr(bsdd_gui, "on_new_project", lambda: None)
    monkeypatch.setattr(tool.MainWindowWidget, "get_active_class", classmethod(lambda cls: None))
    Undo.reset(Undo.serialize(dictionary))
    yield tool.Project
    props.project_dictionary = old_dictionary
    Undo.reset(None)


def _add_class(project, code: str):
    project.get().Classes.append(BsddClass(Code=code, Name=code))


class TestCheckpoint:
    def test_no_checkpoint_without_changes(self, project):
        core_undo.flush(Undo, project)
        assert Undo.can_undo() is False

    def test_change_creates_checkpoint(self, project):
        _add_class(project, "A")
        core_undo.flush(Undo, project)
        assert Undo.can_undo() is True
        assert len(Undo.get_properties().undo_stack) == 1

    def test_rapid_changes_coalesce_into_one_step(self, project):
        _add_class(project, "A")
        _add_class(project, "B")
        core_undo.flush(Undo, project)
        assert len(Undo.get_properties().undo_stack) == 1

    def test_stack_is_capped(self, project):
        for i in range(MAX_STACK_SIZE + 10):
            _add_class(project, f"C{i}")
            core_undo.flush(Undo, project)
        assert len(Undo.get_properties().undo_stack) == MAX_STACK_SIZE


class TestUndoRedo:
    def test_undo_restores_previous_state(self, project):
        _add_class(project, "A")
        core_undo.flush(Undo, project)
        core_undo.perform_undo(Undo, project, tool.MainWindowWidget)
        assert [c.Code for c in project.get().Classes] == []

    def test_redo_restores_undone_state(self, project):
        _add_class(project, "A")
        core_undo.flush(Undo, project)
        core_undo.perform_undo(Undo, project, tool.MainWindowWidget)
        core_undo.perform_redo(Undo, project, tool.MainWindowWidget)
        assert [c.Code for c in project.get().Classes] == ["A"]

    def test_undo_without_history_is_noop(self, project):
        before = project.get()
        core_undo.perform_undo(Undo, project, tool.MainWindowWidget)
        assert project.get() is before

    def test_unsignaled_change_is_caught_on_undo(self, project):
        # No flush, no schedule -- mutation happens silently.
        _add_class(project, "A")
        core_undo.perform_undo(Undo, project, tool.MainWindowWidget)
        assert [c.Code for c in project.get().Classes] == []

    def test_new_change_clears_redo_stack(self, project):
        _add_class(project, "A")
        core_undo.flush(Undo, project)
        core_undo.perform_undo(Undo, project, tool.MainWindowWidget)
        assert Undo.can_redo() is True
        _add_class(project, "B")
        core_undo.flush(Undo, project)
        assert Undo.can_redo() is False

    def test_restored_dictionary_has_parent_refs(self, project):
        _add_class(project, "A")
        core_undo.flush(Undo, project)
        _add_class(project, "B")
        core_undo.flush(Undo, project)
        core_undo.perform_undo(Undo, project, tool.MainWindowWidget)
        restored = project.get()
        assert [c.Code for c in restored.Classes] == ["A"]
        assert all(c.parent() is restored for c in restored.Classes)


class TestReset:
    def test_reset_clears_history(self, project):
        _add_class(project, "A")
        core_undo.flush(Undo, project)
        Undo.reset(Undo.serialize(project.get()))
        assert Undo.can_undo() is False
        assert Undo.can_redo() is False
