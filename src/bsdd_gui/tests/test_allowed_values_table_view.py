"""
Tests for the AllowedValuesTableView module (tool/allowed_values_table_view.py).

The set_* helpers all operate via index.internalPointer() to obtain the
BsddAllowedValue to mutate.  A unittest.mock.MagicMock is used to supply
the internalPointer without a live Qt model.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from bsdd_json.models import BsddAllowedValue
from bsdd_json.utils import dictionary_utils as dict_utils

from bsdd_gui.tool import AllowedValuesTableView


def _mock_index(av: BsddAllowedValue) -> MagicMock:
    index = MagicMock()
    index.internalPointer.return_value = av
    return index


def _null_index() -> MagicMock:
    index = MagicMock()
    index.internalPointer.return_value = None
    return index


# ---------------------------------------------------------------------------
# set_code
# ---------------------------------------------------------------------------

class TestSetCode:
    def test_sets_code(self):
        av = BsddAllowedValue(Code="old", Value="Val")
        AllowedValuesTableView.set_code(None, _mock_index(av), "new-code")
        assert av.Code == "new-code"

    def test_empty_value_is_noop(self):
        av = BsddAllowedValue(Code="old", Value="Val")
        AllowedValuesTableView.set_code(None, _mock_index(av), "")
        assert av.Code == "old"

    def test_none_internal_pointer_does_not_raise(self):
        AllowedValuesTableView.set_code(None, _null_index(), "x")  # must not raise


# ---------------------------------------------------------------------------
# set_value
# ---------------------------------------------------------------------------

class TestSetValue:
    def test_updates_value(self):
        av = BsddAllowedValue(Code="my-code", Value="Old")
        AllowedValuesTableView.set_value(_mock_index(av), "New")
        assert av.Value == "New"

    def test_updates_code_when_code_matches_slugify_of_old_value(self):
        old_value = "My Value"
        av = BsddAllowedValue(Code=dict_utils.slugify(old_value), Value=old_value)
        AllowedValuesTableView.set_value(_mock_index(av), "New Value")
        assert av.Code == dict_utils.slugify("New Value")
        assert av.Value == "New Value"

    def test_does_not_update_code_when_code_differs_from_slugify(self):
        av = BsddAllowedValue(Code="custom-code", Value="Old Value")
        AllowedValuesTableView.set_value(_mock_index(av), "New Value")
        assert av.Code == "custom-code"

    def test_empty_value_is_noop(self):
        av = BsddAllowedValue(Code="c", Value="Old")
        AllowedValuesTableView.set_value(_mock_index(av), "")
        assert av.Value == "Old"

    def test_none_internal_pointer_does_not_raise(self):
        AllowedValuesTableView.set_value(_null_index(), "x")  # must not raise


# ---------------------------------------------------------------------------
# set_description
# ---------------------------------------------------------------------------

class TestSetDescription:
    def test_sets_description(self):
        av = BsddAllowedValue(Code="c", Value="V")
        AllowedValuesTableView.set_description(None, _mock_index(av), "My description")
        assert av.Description == "My description"

    def test_empty_value_sets_none(self):
        av = BsddAllowedValue(Code="c", Value="V", Description="old")
        AllowedValuesTableView.set_description(None, _mock_index(av), "")
        assert av.Description is None


# ---------------------------------------------------------------------------
# set_sort_number
# ---------------------------------------------------------------------------

class TestSetSortNumber:
    def test_sets_sort_number(self):
        av = BsddAllowedValue(Code="c", Value="V")
        AllowedValuesTableView.set_sort_number(None, _mock_index(av), "3")
        assert av.SortNumber == "3"

    def test_empty_value_sets_none(self):
        av = BsddAllowedValue(Code="c", Value="V", SortNumber="1")
        AllowedValuesTableView.set_sort_number(None, _mock_index(av), "")
        assert av.SortNumber is None


# ---------------------------------------------------------------------------
# set_owned_uri
# ---------------------------------------------------------------------------

class TestSetOwnedUri:
    def test_sets_owned_uri(self):
        av = BsddAllowedValue(Code="c", Value="V")
        AllowedValuesTableView.set_owned_uri(None, _mock_index(av), "https://example.com/v")
        assert av.OwnedUri == "https://example.com/v"

    def test_empty_value_sets_none(self):
        av = BsddAllowedValue(Code="c", Value="V", OwnedUri="https://old.com")
        AllowedValuesTableView.set_owned_uri(None, _mock_index(av), "")
        assert av.OwnedUri is None
