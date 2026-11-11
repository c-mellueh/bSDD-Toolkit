"""
Tests for strict inheritance in the desktop app (tool/inheritance.py + core/inheritance.py)
and the project settings file stored next to the project JSON.
"""

from __future__ import annotations

import json

import pytest
from bsdd_json import BsddClass, BsddClassProperty, BsddClassRelation

import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import inheritance as core
from bsdd_gui.core import project as core_project
from bsdd_gui.tool.inheritance import SETTING, Inheritance


def _cp(code: str, pset: str = "Pset_Common", **kw) -> BsddClassProperty:
    return BsddClassProperty(Code=code, PropertyCode=code, PropertySet=pset, **kw)


@pytest.fixture()
def project(dictionary, monkeypatch, qapp):
    props = tool.Project.get_properties()
    old = (props.project_dictionary, props.settings, props.last_saved_settings)
    wall = BsddClass(Code="Wall", Name="Wall", ClassProperties=[_cp("Height"), _cp("Width")])
    inner = BsddClass(Code="InnerWall", Name="Inner Wall", ParentClassCode="Wall")
    fire = BsddClass(Code="EPset_Fire", Name="EPset_Fire", ClassType="GroupOfProperties")
    dictionary.Classes.extend([wall, inner, fire])
    for c in dictionary.Classes:
        c._set_parent(dictionary)
        for cp in c.ClassProperties:
            cp._set_parent(c)
    props.project_dictionary = dictionary
    props.settings = {}
    props.last_saved_settings = {}
    monkeypatch.setattr(bsdd_gui, "on_new_project", lambda: None)
    monkeypatch.setattr(tool.MainWindowWidget, "get", classmethod(lambda cls: None))
    monkeypatch.setattr(tool.MainWindowWidget, "get_active_class", classmethod(lambda cls: None))
    monkeypatch.setattr(tool.MainWindowWidget, "get_active_pset", classmethod(lambda cls: None))
    monkeypatch.setattr(tool.Popups, "request_yes_no", classmethod(lambda cls, *a, **k: True))
    warnings = []
    monkeypatch.setattr(
        tool.Popups, "create_warning_popup", classmethod(lambda cls, *a, **k: warnings.append(a))
    )
    Inheritance.remember(dictionary)
    yield tool.Project, warnings
    props.project_dictionary, props.settings, props.last_saved_settings = old
    Inheritance.remember(None)


def _cls(code: str) -> BsddClass:
    return next(c for c in tool.Project.get().Classes if c.Code == code)


def _switch_on():
    core.set_strict(
        True,
        Inheritance,
        tool.Project,
        tool.Popups,
        tool.MainWindowWidget,
        tool.PropertySetTableView,
        tool.ClassPropertyTableView,
    )


def _check():
    core.check(
        Inheritance,
        tool.Project,
        tool.Undo,
        tool.Popups,
        tool.MainWindowWidget,
        tool.ClassTreeView,
        tool.PropertySetTableView,
        tool.ClassPropertyTableView,
    )


class TestSwitch:
    def test_switching_on_adds_missing_class_properties(self, project):
        _switch_on()
        assert tool.Project.get_setting(SETTING) is True
        assert sorted(cp.Code for cp in _cls("InnerWall").ClassProperties) == ["Height", "Width"]

    def test_declining_leaves_everything_unchanged(self, project, monkeypatch):
        monkeypatch.setattr(tool.Popups, "request_yes_no", classmethod(lambda cls, *a, **k: False))
        _switch_on()
        assert not tool.Project.get_setting(SETTING)
        assert _cls("InnerWall").ClassProperties == []

    def test_off_by_default_does_nothing(self, project):
        _cls("Wall").ClassProperties.append(_cp("Length"))
        _check()
        assert _cls("InnerWall").ClassProperties == []


class TestCheck:
    def test_new_parent_property_is_passed_on(self, project):
        _switch_on()
        wall = _cls("Wall")
        cp = _cp("Length")
        cp._set_parent(wall)
        wall.ClassProperties.append(cp)
        _check()
        assert "Length" in [cp.Code for cp in _cls("InnerWall").ClassProperties]

    def test_removing_inherited_property_in_child_is_undone(self, project):
        _, warnings = project
        _switch_on()
        inner = _cls("InnerWall")
        inner.ClassProperties[:] = [cp for cp in inner.ClassProperties if cp.Code != "Height"]
        _check()
        assert "Height" in [cp.Code for cp in _cls("InnerWall").ClassProperties]
        assert len(warnings) == 1
        assert "inherited from 'Wall'" in warnings[0][0]

    def test_child_can_change_values(self, project):
        _, warnings = project
        _switch_on()
        inner = _cls("InnerWall")
        inner.ClassProperties[0].IsRequired = True
        _check()
        assert warnings == []
        assert _cls("InnerWall").ClassProperties[0].IsRequired is True

    def test_gop_link_is_inherited(self, project):
        _switch_on()
        wall = _cls("Wall")
        uri = "https://identifier.buildingsmart.org/uri/tst/test_dict/1.0/class/EPset_Fire"
        rel = BsddClassRelation(RelationType="HasReference", RelatedClassUri=uri)
        rel._set_parent(wall)
        wall.ClassRelations.append(rel)
        _check()
        assert [r.RelationType for r in _cls("InnerWall").ClassRelations] == ["HasReference"]


class TestSettingsFile:
    def test_path_next_to_project(self):
        assert tool.Project.get_settings_path("/a/b/dict.json") == "/a/b/dict.bsdd-toolkit.json"

    def test_default_settings_write_no_file(self, project, tmp_path):
        path = str(tmp_path / "dict.json")
        tool.Project.write_settings(path)
        assert not (tmp_path / "dict.bsdd-toolkit.json").exists()

    def test_round_trip(self, project, tmp_path):
        path = str(tmp_path / "dict.json")
        tool.Project.set_setting(SETTING, True)
        assert tool.Project.settings_changed_since_save()
        tool.Project.write_settings(path)
        assert not tool.Project.settings_changed_since_save()
        data = json.loads((tmp_path / "dict.bsdd-toolkit.json").read_text())
        assert data == {"strict_inheritance": True}
        assert tool.Project.read_settings(path) == {"strict_inheritance": True}

    def test_broken_file_is_ignored(self, tmp_path):
        (tmp_path / "dict.bsdd-toolkit.json").write_text("{nope")
        assert tool.Project.read_settings(str(tmp_path / "dict.json")) == {}

    def test_save_project_writes_settings(self, project, tmp_path, monkeypatch):
        # keep the user's recent/open paths untouched
        for name in ("set_path", "add_path"):
            monkeypatch.setattr(tool.Appdata, name, classmethod(lambda cls, *a, **k: None))
        tool.Project.set_setting(SETTING, True)
        path = str(tmp_path / "dict.json")
        core_project.save_project(path, tool.Project, tool.Appdata)
        assert (tmp_path / "dict.bsdd-toolkit.json").exists()
