from __future__ import annotations
from bsdd_gui.presets.prop_presets import FieldProperties,ActionsProperties
from bsdd import Client

class DownloadProperties(FieldProperties,ActionsProperties):
    def __init__(self):
        super().__init__()
        self.client:Client = None
