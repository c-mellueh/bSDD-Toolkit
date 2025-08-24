from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


class LanguageProperties:
    widget: ui.SettingsWidget = None
    current_language = None
