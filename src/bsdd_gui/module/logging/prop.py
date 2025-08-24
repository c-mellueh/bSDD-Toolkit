from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.tool.logging import Signaller
    from . import ui


class LoggingProperties:
    log_path: str = None
    log_format = "%(asctime)s | %(levelname)6s | %(module_func)50s [%(lineno)04d] |  %(message)s"
    log_level = None
    custom_formatter = None
    ignore_texts = list()
    signaller: Signaller = None
    settings_widget: ui.SettingsWidget = None
