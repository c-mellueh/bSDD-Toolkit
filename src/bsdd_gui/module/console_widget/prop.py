from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ui import Console


class ConsoleWidgetProperties:
    console: Console = None
