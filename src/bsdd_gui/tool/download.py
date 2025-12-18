from __future__ import annotations
from typing import TYPE_CHECKING, Type
from types import ModuleType
from bsdd import Client
from bsdd_json import BsddDictionary,BsddClass,BsddProperty
import logging
from bsdd_gui.presets.tool_presets import FieldTool, ActionTool
import bsdd_gui
from bsdd_json.utils import class_utils
from bsdd_json.utils import property_utils as prop_utils

from bsdd_gui.module.download import ui, trigger

if TYPE_CHECKING:
    from bsdd_gui.module.download.prop import DownloadProperties


class Download(FieldTool, ActionTool):
    @classmethod
    def get_properties(cls) -> DownloadProperties:
        return bsdd_gui.DownloadProperties

    @classmethod
    def _get_trigger(cls) -> ModuleType:
        return trigger

    @classmethod
    def _get_widget_class(cls) -> Type[ui.DownloadWidget]:
        return ui.DownloadWidget

    @classmethod
    def get_client(cls) -> Client:
        client = cls.get_properties().client
        if not client:
            cls.get_properties().client = Client()
        return cls.get_properties().client

    @classmethod
    def swap_codes(cls, data_dict:dict, old:str, new:str):
        if old not in data_dict:
            return
        data_dict[new] = data_dict[old]
        data_dict.pop(old)

    @classmethod
    def import_dictionary(cls, dictionary_uri):
        def read_lang_code():
            if "availableLanguages" not in dictionary_data:
                return
            dictionary_data.pop("availableLanguages")

        dictionary_data = cls.get_client().get_dictionary(dictionary_uri)["dictionaries"][0]
        read_lang_code()
        cls.swap_codes(dictionary_data, "organizationCodeOwner", "OrganizationCode")
        cls.swap_codes(dictionary_data, "code", "DictionaryCode")
        cls.swap_codes(dictionary_data, "version", "DictionaryVersion")
        cls.swap_codes(dictionary_data, "defaultLanguageCode", "LanguageIsoCode")
        cls.swap_codes(dictionary_data, "name", "DictionaryName")
        cls.swap_codes(dictionary_data, "changeRequestEmail", "ChangeRequestEmailAddress")
        dictionary_data["LanguageOnly"] = False
        dictionary_data["UseOwnUri"] = False
        return BsddDictionary.model_validate(dictionary_data)

    @classmethod
    def get_all_classes(cls, dictionary_uri: str, bsdd_dictionary: BsddDictionary):
        classes_info = list()
        class_count = 0
        total_count = None
        while total_count is None or class_count < total_count:
            cd = cls.get_client().get_classes(
                dictionary_uri, use_nested_classes=False, limit=1_000, offset=class_count
            )
            classes_info += cd["classes"]
            class_count += cd["classesCount"]
            total_count = cd["classesTotalCount"]
        loaded_classes = list()

        loaded_classes.append(
                class_utils.load_class(c["uri"], bsdd_dictionary, True, True, client)
            )
        return loaded_classes

    @classmethod
    def get_all_properties(cls, dictionary_uri):
        property_info = list()
        property_count = 0
        total_count = None
        while total_count is None or property_count < total_count:
            pd = cls.get_client().get_properties(dictionary_uri, limit=1000, offset=property_count)
            property_info += pd["properties"]
            property_count += pd["propertiesCount"]
            total_count = pd["propertiesTotalCount"]

        loaded_properties = list()
        for p in property_info, "Load Properties":
            loaded_properties.append(prop_utils.load_property(p["uri"], client=cls.get_client()))
        return loaded_properties
