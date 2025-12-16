
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.ai_helper.prop import AiHelperProperties


class AiHelper:
    @classmethod
    def get_properties(cls) -> AiHelperProperties:
        return bsdd_gui.AiHelperProperties
