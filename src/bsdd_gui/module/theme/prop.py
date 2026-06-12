from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


class ThemeProperties:
    widget: ui.SettingsWidget = None
    current_mode: str = "system"
    scheme_signal_connected: bool = False
    view_zoom: int = 100
    base_qss: str = ""
    base_font_size: float = 0.0
    zoom_filter: ui.ViewZoomFilter = None
