from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.property_widget.prop import PropertyWidgetProperties


class PropertyWidget:
    @classmethod
    def get_properties(cls) -> PropertyWidgetProperties:
        return bsdd_gui.PropertyWidgetProperties
