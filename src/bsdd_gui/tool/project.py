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
from PySide6.QtWidgets import QMenu
from bsdd_gui.module.project import trigger

if TYPE_CHECKING:
    from bsdd_gui.module.project.prop import ProjectProperties


class Signals(QObject):
    open_requested = Signal(object)
    new_requested = Signal()
    save_requested = Signal()
    save_as_requested = Signal()
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
    ifc_relation_addded = Signal(BsddClass, str)  # IfcRelationName
    ifc_relation_removed = Signal(BsddClass, str)  # IfcRelationName
    recent_menu_about_to_show = Signal()


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
    def connect_internal_signals(cls):
        cls.signals.save_requested.connect(trigger.save_clicked)
        cls.signals.save_as_requested.connect(trigger.save_as_clicked)
        cls.signals.open_requested.connect(trigger.open_clicked)
        cls.signals.new_requested.connect(trigger.new_clicked)
        cls.signals.recent_menu_about_to_show.connect(trigger.populate_recent_menu)
        return super().connect_internal_signals()

    @classmethod
    def register_project(cls, bsdd_dictionary: BsddDictionary):
        cls.get_properties().project_dictionary = bsdd_dictionary
        cls.set_last_save(bsdd_dictionary)
        bsdd_gui.on_new_project()

    @classmethod
    def load_project(cls, path: os.PathLike, sloppy=False):
        if not path:
            return
        prop = cls.get_properties()
        prop.project_dictionary = BsddDictionary.load(path, sloppy=sloppy)
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

    @classmethod
    def set_offline_mode(cls, mode: bool):
        cls.get_properties().offline_mode = mode

    @classmethod
    def get_offline_mode(cls) -> bool:
        return cls.get_properties().offline_mode

    @classmethod
    def set_last_save(cls, bsdd_dictionary: BsddDictionary):
        cls.get_properties().last_save = bsdd_dictionary.model_copy(deep=True)

    @classmethod
    def get_last_save(cls) -> BsddDictionary:
        return cls.get_properties().last_save

    @classmethod
    def request_save(cls):
        cls.signals.save_requested.emit()

    @classmethod
    def request_save_as(cls):
        cls.signals.save_as_requested.emit()

    @classmethod
    def request_open(cls,path = None):
        cls.signals.open_requested.emit(path)

    @classmethod
    def request_new(cls):
        cls.signals.new_requested.emit()

    # Recent Menu
    @classmethod
    def set_recent_menu(cls, recent_menu: QMenu):
        cls.get_properties().recent_menu = recent_menu
        recent_menu.aboutToShow.connect(cls.signals.recent_menu_about_to_show.emit)

    @classmethod
    def get_recent_menu(cls) -> QMenu:
        return cls.get_properties().recent_menu
    
