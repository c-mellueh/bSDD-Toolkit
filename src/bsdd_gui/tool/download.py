
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.download.prop import DownloadProperties


class Download:
    @classmethod
    def get_properties(cls) -> DownloadProperties:
        return bsdd_gui.DownloadProperties
