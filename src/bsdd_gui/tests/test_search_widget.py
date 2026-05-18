"""
Tests for the SearchWidget module (tool/search_widget.py).

Tests cover the pure helpers that do not require a live Qt dialog.
"""
from __future__ import annotations

from bsdd_gui.tool import SearchWidget


# ---------------------------------------------------------------------------
# 1. get_column_texts
# ---------------------------------------------------------------------------

class TestGetColumnTexts:
    def test_class_mode_returns_three_columns(self):
        cols = SearchWidget.get_column_texts(1)
        assert len(cols) == 3

    def test_property_mode_returns_two_columns(self):
        cols = SearchWidget.get_column_texts(2)
        assert len(cols) == 2

    def test_class_mode_columns_are_strings(self):
        for col in SearchWidget.get_column_texts(1):
            assert isinstance(col, str)

    def test_property_mode_columns_are_strings(self):
        for col in SearchWidget.get_column_texts(2):
            assert isinstance(col, str)


# ---------------------------------------------------------------------------
# 2. get_threshold
# ---------------------------------------------------------------------------

class TestGetThreshold:
    def test_threshold_is_integer(self):
        assert isinstance(SearchWidget.get_threshold(), int)

    def test_threshold_is_positive(self):
        assert SearchWidget.get_threshold() > 0
