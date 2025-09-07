from __future__ import annotations
from typing import TYPE_CHECKING, Any
import logging
import os
import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool
from bsdd_json import (
    BsddDictionary,
    BsddClass,
    BsddProperty,
    BsddClassProperty,
    BsddClassRelation,
    BsddPropertyRelation,
)
from bsdd_gui.module.project import ui
from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from bsdd_gui.module.project.prop import ProjectProperties


class Signals(QObject):
    data_changed = Signal(str, object)  # name of datafield, new_value
    class_added = Signal(BsddClass)
    class_removed = Signal(BsddClass)
    class_property_added = Signal(BsddClassProperty)
    class_property_removed = Signal(BsddClassProperty)
    property_added = Signal(BsddProperty)
    property_removed = Signal(BsddProperty)
    class_relation_added = Signal(BsddClassRelation)
    class_relation_removed = Signal(BsddClassRelation)
    property_relation_added = Signal(BsddPropertyRelation)
    property_relation_removed = Signal(BsddPropertyRelation)


class Project(ActionTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> ProjectProperties:
        return bsdd_gui.ProjectProperties

    @classmethod
    def create_project(cls, input_dict: dict[str, str | bool] = None):
        new_dict = BsddDictionary(
            OrganizationCode="default",
            DictionaryCode="default",
            DictionaryName="default",
            DictionaryVersion="0.0.1",
            LanguageIsoCode="de-DE",
            LanguageOnly=False,
            UseOwnUri=False,
        )
        if input_dict:
            new_dict = BsddDictionary(**input_dict)
        return new_dict

    @classmethod
    def register_project(cls, bsdd_dictionary: BsddDictionary):
        cls.get_properties().project_dictionary = bsdd_dictionary
        bsdd_gui.on_new_project()

    @classmethod
    def load_project(cls, path: os.PathLike):
        prop = cls.get_properties()
        prop.project_dictionary = BsddDictionary.load(path)
        return prop.project_dictionary

    @classmethod
    def get(cls) -> BsddDictionary:
        return cls.get_properties().project_dictionary

    @classmethod
    def create_new_project_widget(cls, parent) -> ui.NewDialog:
        cls.get_properties().dialog = ui.NewDialog(parent)
        return cls.get_properties().dialog

    @classmethod
    def add_plugin_save_function(cls, func: callable) -> int:
        """
        add Function that gets called before Project is saved to JSON
        """
        cls.get_properties().plugin_save_functions.append(func)
        return len(cls.get_properties().plugin_save_functions) - 1

    @classmethod
    def remove_plugin_save_function(cls, index: int):
        cls.get_properties().plugin_save_functions[index] = None

    @classmethod
    def get_plugin_save_functions(cls):
        return cls.get_properties().plugin_save_functions
