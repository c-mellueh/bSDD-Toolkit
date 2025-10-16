
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.ids_exporter.prop import IdsExporterProperties


class IdsExporter:
    @classmethod
    def get_properties(cls) -> IdsExporterProperties:
        return bsdd_gui.IdsExporterProperties
