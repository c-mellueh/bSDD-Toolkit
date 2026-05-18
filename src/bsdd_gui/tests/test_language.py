"""
Tests for the Language module (tool/language.py).

Covers the get/set language state helpers.
"""

from __future__ import annotations

import pytest
from bsdd_gui.tool import Language


@pytest.fixture(autouse=True)
def _restore_language():
    original = Language.get_language()
    yield
    Language.set_language(original)


class TestLanguage:
    def test_set_and_get_language(self):
        Language.set_language("en-GB")
        assert Language.get_language() == "en-GB"

    def test_set_different_language(self):
        Language.set_language("de")
        assert Language.get_language() == "de"

    def test_set_language_roundtrip(self):
        for code in ("en-US", "fr", "nl-BE"):
            Language.set_language(code)
            assert Language.get_language() == code
