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
    old_zoom = Theme.get_view_zoom()
    yield
    Theme.set_mode(old_mode)
    Theme.set_view_zoom(old_zoom)


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


class TestValidationStyles:
    @pytest.mark.parametrize("scheme", ["light", "dark"])
    def test_invalid_rules_are_part_of_base_stylesheet(self, scheme):
        from bsdd_gui.tool.theme import ICON_TOKENS

        tokens = Theme.get_tokens(scheme)
        tokens.update({name: "icon.svg" for name in ICON_TOKENS})
        qss = Theme.build_stylesheet(tokens)
        assert 'QLineEdit[invalid="true"]' in qss
        assert tokens["error"] in qss


class TestActiveTokens:
    def test_rgba_helper(self):
        from bsdd_gui.tool.theme import rgba

        assert rgba("#FF0000", 128) == "rgba(255, 0, 0, 128)"

    def test_active_tokens_after_apply(self, qapp, icon_cache):
        old_sheet = qapp.styleSheet()
        try:
            Theme.apply_theme(qapp, "dark")
            assert Theme.get_active_tokens()["window"] == styles.DARK_TOKENS["window"]
        finally:
            qapp.setStyleSheet(old_sheet)

    def test_theme_changed_signal_emitted(self, qapp, icon_cache):
        received = []
        slot = lambda: received.append(True)  # noqa: E731
        Theme.signals.theme_changed.connect(slot)
        old_sheet = qapp.styleSheet()
        try:
            Theme.apply_theme(qapp, "light")
        finally:
            Theme.signals.theme_changed.disconnect(slot)
            qapp.setStyleSheet(old_sheet)
        assert len(received) == 1


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


class TestViewZoom:
    def test_zoom_is_clamped(self):
        from bsdd_gui.tool.theme import VIEW_ZOOM_MAX, VIEW_ZOOM_MIN

        Theme.set_view_zoom(10)
        assert Theme.get_view_zoom() == VIEW_ZOOM_MIN
        Theme.set_view_zoom(9999)
        assert Theme.get_view_zoom() == VIEW_ZOOM_MAX

    def test_default_zoom_adds_no_rule(self, qapp):
        assert Theme.build_view_zoom_rule(qapp, 100) == ""

    def test_zoom_rule_scales_view_fonts(self, qapp):
        rule = Theme.build_view_zoom_rule(qapp, 150)
        assert "QTreeView" in rule and "QTableView" in rule
        assert "font-size" in rule

    def test_apply_view_zoom_appends_rule(self, qapp, icon_cache):
        old_sheet = qapp.styleSheet()
        try:
            Theme.apply_theme(qapp, "light")
            Theme.set_view_zoom(150)
            Theme.apply_view_zoom(qapp)
            assert "font-size" in qapp.styleSheet()
            Theme.set_view_zoom(100)
            Theme.apply_view_zoom(qapp)
            assert qapp.styleSheet() == Theme.get_properties().base_qss
        finally:
            qapp.setStyleSheet(old_sheet)


class TestViewZoomFilter:
    @pytest.fixture()
    def tree(self, qapp):
        from PySide6.QtWidgets import QTreeWidget

        tree = QTreeWidget()
        yield tree
        tree.deleteLater()

    @staticmethod
    def _wheel_event(delta_y: int, modifiers):
        from PySide6.QtCore import QPoint, QPointF, Qt
        from PySide6.QtGui import QWheelEvent

        return QWheelEvent(
            QPointF(5, 5),
            QPointF(5, 5),
            QPoint(0, 0),
            QPoint(0, delta_y),
            Qt.MouseButton.NoButton,
            modifiers,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )

    def test_ctrl_wheel_over_view_triggers_zoom(self, tree, monkeypatch):
        from PySide6.QtCore import Qt

        from bsdd_gui.module.theme import trigger, ui

        steps = []
        monkeypatch.setattr(trigger, "view_zoom_scrolled", steps.append)
        event_filter = ui.ViewZoomFilter()
        event = self._wheel_event(120, Qt.KeyboardModifier.ControlModifier)
        assert event_filter.eventFilter(tree.viewport(), event) is True
        assert steps == [1]

    def test_wheel_without_ctrl_is_ignored(self, tree, monkeypatch):
        from PySide6.QtCore import Qt

        from bsdd_gui.module.theme import trigger, ui

        steps = []
        monkeypatch.setattr(trigger, "view_zoom_scrolled", steps.append)
        event_filter = ui.ViewZoomFilter()
        event = self._wheel_event(120, Qt.KeyboardModifier.NoModifier)
        assert event_filter.eventFilter(tree.viewport(), event) is False
        assert steps == []

    def test_ctrl_wheel_outside_views_is_ignored(self, qapp, monkeypatch):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QLineEdit

        from bsdd_gui.module.theme import trigger, ui

        steps = []
        monkeypatch.setattr(trigger, "view_zoom_scrolled", steps.append)
        line_edit = QLineEdit()
        event_filter = ui.ViewZoomFilter()
        event = self._wheel_event(120, Qt.KeyboardModifier.ControlModifier)
        assert event_filter.eventFilter(line_edit, event) is False
        assert steps == []
        line_edit.deleteLater()
