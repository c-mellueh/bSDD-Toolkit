"""
Tests for the Theme module (tool/theme.py).

Covers token parity between the light and dark palettes, QSS template
rendering, scheme resolution, and a full apply_theme round-trip on the
offscreen QApplication.
"""

from __future__ import annotations

import pytest
from PySide6.QtGui import QPalette

from bsdd_gui.module.theme import styles
from bsdd_gui.tool import Theme


@pytest.fixture(autouse=True)
def _restore_mode():
    old_mode = Theme.get_mode()
    yield
    Theme.set_mode(old_mode)


@pytest.fixture()
def icon_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(Theme, "get_icon_cache_dir", classmethod(lambda cls: str(tmp_path)))
    return tmp_path


class TestTokens:
    def test_light_and_dark_define_same_keys(self):
        assert set(styles.LIGHT_TOKENS) == set(styles.DARK_TOKENS)

    def test_get_tokens_returns_copy(self):
        tokens = Theme.get_tokens("light")
        tokens["window"] = "changed"
        assert styles.LIGHT_TOKENS["window"] != "changed"


class TestStylesheet:
    @pytest.mark.parametrize("scheme", ["light", "dark"])
    def test_all_placeholders_substituted(self, scheme):
        from bsdd_gui.tool.theme import ICON_TOKENS

        tokens = Theme.get_tokens(scheme)
        tokens.update({name: "icon.svg" for name in ICON_TOKENS})
        qss = Theme.build_stylesheet(tokens)
        assert "$" not in qss

    def test_unknown_token_raises(self):
        with pytest.raises(KeyError):
            Theme.build_stylesheet({})


class TestSchemeResolution:
    def test_explicit_modes_win_over_system(self, qapp):
        assert Theme.resolve_scheme(qapp, "light") == "light"
        assert Theme.resolve_scheme(qapp, "dark") == "dark"

    def test_system_mode_resolves_to_concrete_scheme(self, qapp):
        assert Theme.resolve_scheme(qapp, "system") in ("light", "dark")

    def test_invalid_mode_falls_back_to_system(self):
        Theme.set_mode("purple")
        assert Theme.get_mode() == "system"


class TestPalette:
    def test_palette_matches_tokens(self):
        tokens = Theme.get_tokens("dark")
        palette = Theme.build_palette(tokens)
        assert palette.color(QPalette.ColorRole.Window).name().lower() == tokens["window"].lower()
        assert palette.color(QPalette.ColorRole.Base).name().lower() == tokens["surface"].lower()
        assert (
            palette.color(QPalette.ColorRole.Highlight).name().lower() == tokens["accent"].lower()
        )


class TestApplyTheme:
    @pytest.mark.parametrize("mode", ["light", "dark"])
    def test_apply_sets_stylesheet_and_writes_icons(self, qapp, icon_cache, mode):
        old_sheet = qapp.styleSheet()
        try:
            Theme.apply_theme(qapp, mode)
            assert qapp.styleSheet()
            assert "$" not in qapp.styleSheet()
            assert list(icon_cache.glob("*.svg"))
        finally:
            qapp.setStyleSheet(old_sheet)
