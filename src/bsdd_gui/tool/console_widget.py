from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.module.console_widget import ui

if TYPE_CHECKING:
    from bsdd_gui.module.console_widget.prop import ConsoleWidgetProperties


class ConsoleWidget:
    @classmethod
    def get_properties(cls) -> ConsoleWidgetProperties:
        return bsdd_gui.ConsoleProperties

    @classmethod
    def create_console(cls):
        if cls.get_properties().console is None:
            console = ui.Console()
            console.show()
            console.eval_in_thread()
            cls.get_properties().console = console
        return cls.get_properties().console

    @classmethod
    def close_console(cls):
        logging.debug("Close Console")
        cls.get_properties().console = None
