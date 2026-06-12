from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


class ThemeProperties:
    widget: ui.SettingsWidget = None
    current_mode: str = "system"
    scheme_signal_connected: bool = False
