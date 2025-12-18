from __future__ import annotations
from bsdd_gui.presets.prop_presets import FieldProperties,ActionsProperties
from bsdd import Client
from bsdd_json import BsddDictionary
class DownloadProperties(FieldProperties,ActionsProperties):
    def __init__(self):
        super().__init__()
        self.client:Client = None
        self.threads = list()
        self.workers = list()
        self.done_count = 0
        self.bsdd_classes = list()
        self.bsdd_dictionary:BsddDictionary = None
        self.bsdd_properies = list()    
        self.save_path = "export.json"