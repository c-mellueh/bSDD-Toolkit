
from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_json import BsddDictionary,BsddClass,BsddProperty
import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool
if TYPE_CHECKING:
    from bsdd_gui.module.ids_exporter.prop import IdsExporterProperties
from bsdd_gui.module.ids_exporter import trigger


class IdsExporter(ActionTool):
    @classmethod
    def get_properties(cls) -> IdsExporterProperties:
        return bsdd_gui.IdsExporterProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
    
    @classmethod
    def build_ids(cls,bsdd_dict:BsddDictionary):
        out_path = "test.ids"

        