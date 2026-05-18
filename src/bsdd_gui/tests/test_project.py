"""
Tests for the Project module (tool/project.py).

Tests cover pure data-model operations only (create, load, offline mode,
plugin save functions, last-save tracking).  Signal-heavy UI operations are
out of scope here.
"""
from __future__ import annotations

import json

from bsdd_json.models import BsddDictionary

from bsdd_gui.tool import Project


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _minimal_dict_data(**overrides) -> dict:
    base = {
        "OrganizationCode": "TST",
        "DictionaryCode": "TEST",
        "DictionaryVersion": "1.0",
        "LanguageIsoCode": "en-GB",
        "LanguageOnly": False,
        "UseOwnUri": False,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. create_project
# ---------------------------------------------------------------------------

class TestCreateProject:
    def test_returns_bsdd_dictionary(self):
        d = Project.create_project()
        assert isinstance(d, BsddDictionary)

    def test_default_dictionary_code(self):
        d = Project.create_project()
        assert d.DictionaryCode == "default"

    def test_default_version(self):
        d = Project.create_project()
        assert d.DictionaryVersion == "0.0.1"

    def test_accepts_input_dict(self):
        d = Project.create_project(_minimal_dict_data(DictionaryCode="CUSTOM"))
        assert d.DictionaryCode == "CUSTOM"

    def test_input_dict_overrides_defaults(self):
        d = Project.create_project(_minimal_dict_data(DictionaryVersion="9.9.9"))
        assert d.DictionaryVersion == "9.9.9"


# ---------------------------------------------------------------------------
# 2. load_project
# ---------------------------------------------------------------------------

class TestLoadProject:
    def test_loads_json_file(self, tmp_path):
        data = _minimal_dict_data(DictionaryCode="LOADED")
        path = tmp_path / "test.json"
        path.write_text(json.dumps(data))

        d = Project.load_project(str(path))
        assert isinstance(d, BsddDictionary)
        assert d.DictionaryCode == "LOADED"

    def test_returns_none_for_empty_path(self):
        assert Project.load_project("") is None
        assert Project.load_project(None) is None

    def test_loaded_project_has_correct_classes(self, tmp_path):
        data = _minimal_dict_data()
        data["classes"] = [{"code": "CLS1", "name": "Class 1", "classType": "Class"}]
        path = tmp_path / "with_classes.json"
        path.write_text(json.dumps(data))

        d = Project.load_project(str(path))
        assert len(d.Classes) == 1
        assert d.Classes[0].Code == "CLS1"


# ---------------------------------------------------------------------------
# 3. offline_mode
# ---------------------------------------------------------------------------

class TestOfflineMode:
    def test_default_is_false(self):
        # Reset to known state
        Project.set_offline_mode(False)
        assert Project.get_offline_mode() is False

    def test_set_true(self):
        Project.set_offline_mode(True)
        assert Project.get_offline_mode() is True
        Project.set_offline_mode(False)  # restore

    def test_roundtrip(self):
        for value in (True, False):
            Project.set_offline_mode(value)
            assert Project.get_offline_mode() is value


# ---------------------------------------------------------------------------
# 4. plugin_save_functions
# ---------------------------------------------------------------------------

class TestPluginSaveFunctions:
    def test_add_returns_index(self):
        initial = len(Project.get_plugin_save_functions())
        idx = Project.add_plugin_save_function(lambda: None)
        assert idx == initial

    def test_function_is_retrievable(self):
        func = lambda: "sentinel"
        idx = Project.add_plugin_save_function(func)
        assert Project.get_plugin_save_functions()[idx] is func

    def test_remove_sets_slot_to_none(self):
        idx = Project.add_plugin_save_function(lambda: None)
        Project.remove_plugin_save_function(idx)
        assert Project.get_plugin_save_functions()[idx] is None


# ---------------------------------------------------------------------------
# 5. set_last_save / get_last_save
# ---------------------------------------------------------------------------

class TestLastSave:
    def test_last_save_is_deep_copy(self):
        d = BsddDictionary(**_minimal_dict_data())
        Project.set_last_save(d)
        last = Project.get_last_save()
        assert last is not d

    def test_last_save_has_same_code(self):
        d = BsddDictionary(**_minimal_dict_data(DictionaryCode="SNAP"))
        Project.set_last_save(d)
        assert Project.get_last_save().DictionaryCode == "SNAP"

    def test_mutating_original_does_not_affect_last_save(self):
        d = BsddDictionary(**_minimal_dict_data(DictionaryCode="ORIG"))
        Project.set_last_save(d)
        d.DictionaryCode = "CHANGED"
        assert Project.get_last_save().DictionaryCode == "ORIG"
