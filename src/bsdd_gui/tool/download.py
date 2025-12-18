from __future__ import annotations
from typing import TYPE_CHECKING, Type
from types import ModuleType

import logging
from bsdd_gui.presets.tool_presets import FieldTool,ActionTool
import bsdd_gui
from bsdd_gui.module.download import ui, trigger

if TYPE_CHECKING:
    from bsdd_gui.module.download.prop import DownloadProperties


class Download(FieldTool,ActionTool):
    @classmethod
    def get_properties(cls) -> DownloadProperties:
        return bsdd_gui.DownloadProperties

    @classmethod
    def _get_trigger(cls) -> ModuleType:
        return trigger

    @classmethod
    def _get_widget_class(cls) -> Type[ui.DownloadWidget]:
        return ui.DownloadWidget
