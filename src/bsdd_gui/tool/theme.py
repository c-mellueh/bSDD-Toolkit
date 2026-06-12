from __future__ import annotations

import logging
import os
from string import Template
from typing import TYPE_CHECKING, Callable

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

import bsdd_gui
from bsdd_gui.module.theme import styles

if TYPE_CHECKING:
    from bsdd_gui.module.theme.prop import ThemeProperties
    from bsdd_gui.module.theme import ui

# icon token name -> (svg template name, color token)
ICON_TOKENS = {
    "icon_chevron_down": ("chevron_down", "text_muted"),
    "icon_chevron_up": ("chevron_up", "text_muted"),
    "icon_chevron_right": ("chevron_right", "text_muted"),
    "icon_check": ("check", "on_accent"),
}

MODES = ("system", "light", "dark")


class Theme:
    @classmethod
    def get_properties(cls) -> ThemeProperties:
        return bsdd_gui.ThemeProperties

    @classmethod
    def get_widget(cls) -> ui.SettingsWidget | None:
        return cls.get_properties().widget

    @classmethod
    def set_widget(cls, widget: ui.SettingsWidget) -> None:
        cls.get_properties().widget = widget

    @classmethod
    def get_mode(cls) -> str:
        return cls.get_properties().current_mode

    @classmethod
    def set_mode(cls, mode: str) -> None:
        if mode not in MODES:
            mode = "system"
        cls.get_properties().current_mode = mode

    @classmethod
    def resolve_scheme(cls, app: QApplication, mode: str) -> str:
        """Map a user mode (system/light/dark) to the concrete scheme."""
        if mode in ("light", "dark"):
            return mode
        if app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            return "dark"
        return "light"

    @classmethod
    def get_tokens(cls, scheme: str) -> dict[str, str]:
        return dict(styles.DARK_TOKENS if scheme == "dark" else styles.LIGHT_TOKENS)

    @classmethod
    def build_stylesheet(cls, tokens: dict[str, str]) -> str:
        return Template(styles.QSS_TEMPLATE).substitute(tokens)

    @classmethod
    def build_palette(cls, tokens: dict[str, str]) -> QPalette:
        palette = QPalette()
        roles = {
            QPalette.ColorRole.Window: tokens["window"],
            QPalette.ColorRole.WindowText: tokens["text"],
            QPalette.ColorRole.Base: tokens["surface"],
            QPalette.ColorRole.AlternateBase: tokens["surface_alt"],
            QPalette.ColorRole.Text: tokens["text"],
            QPalette.ColorRole.PlaceholderText: tokens["text_muted"],
            QPalette.ColorRole.Button: tokens["button"],
            QPalette.ColorRole.ButtonText: tokens["text"],
            QPalette.ColorRole.Highlight: tokens["accent"],
            QPalette.ColorRole.HighlightedText: tokens["on_accent"],
            QPalette.ColorRole.ToolTipBase: tokens["tooltip_bg"],
            QPalette.ColorRole.ToolTipText: tokens["tooltip_text"],
            QPalette.ColorRole.Link: tokens["link"],
            QPalette.ColorRole.BrightText: tokens["accent_hover"],
        }
        for role, value in roles.items():
            palette.setColor(role, QColor(value))
        disabled = QColor(tokens["text_disabled"])
        for role in (
            QPalette.ColorRole.WindowText,
            QPalette.ColorRole.Text,
            QPalette.ColorRole.ButtonText,
            QPalette.ColorRole.HighlightedText,
        ):
            palette.setColor(QPalette.ColorGroup.Disabled, role, disabled)
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.Highlight,
            QColor(tokens["surface_sunken"]),
        )
        return palette

    @classmethod
    def get_icon_cache_dir(cls) -> str:
        from bsdd_gui import tool

        return os.path.join(tool.Appdata.get_appdata_folder(), "theme_icons")

    @classmethod
    def build_icon_tokens(cls, tokens: dict[str, str]) -> dict[str, str]:
        """Write palette-tinted SVGs to the cache dir and return url-ready paths."""
        cache_dir = cls.get_icon_cache_dir()
        os.makedirs(cache_dir, exist_ok=True)
        icon_tokens = {}
        for token_name, (svg_name, color_token) in ICON_TOKENS.items():
            color = tokens[color_token]
            file_name = f"{svg_name}_{color.lstrip('#').lower()}.svg"
            path = os.path.join(cache_dir, file_name)
            if not os.path.exists(path):
                svg = Template(styles.SVG_TEMPLATES[svg_name]).substitute(color=color)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(svg)
            icon_tokens[token_name] = path.replace("\\", "/")
        return icon_tokens

    @classmethod
    def apply_theme(cls, app: QApplication, mode: str) -> None:
        scheme = cls.resolve_scheme(app, mode)
        logging.info(f"Applying '{scheme}' theme (mode '{mode}')")
        tokens = cls.get_tokens(scheme)
        tokens.update(cls.build_icon_tokens(tokens))
        app.setStyle("Fusion")
        app.setPalette(cls.build_palette(tokens))
        app.setStyleSheet(cls.build_stylesheet(tokens))
        cls._set_icon_defaults(tokens)

    @classmethod
    def _set_icon_defaults(cls, tokens: dict[str, str]) -> None:
        qta.set_defaults(color=tokens["text"], color_disabled=tokens["text_disabled"])
        if hasattr(qta, "reset_cache"):
            qta.reset_cache()

    @classmethod
    def connect_color_scheme_signal(cls, app: QApplication, callback: Callable) -> None:
        props = cls.get_properties()
        if props.scheme_signal_connected:
            return
        app.styleHints().colorSchemeChanged.connect(callback)
        props.scheme_signal_connected = True
