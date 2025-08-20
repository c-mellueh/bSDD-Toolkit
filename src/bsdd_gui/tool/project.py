from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import os
import bsdd_gui
import bsdd_parser.models

if TYPE_CHECKING:
    from bsdd_gui.module.project.prop import ProjectProperties


class Project:
    @classmethod
    def get_properties(cls) -> ProjectProperties:
        return bsdd_gui.ProjectProperties

    @classmethod
    def create_project(cls):
        cls.get_properties().project_dictionary = bsdd_parser.models.BsddDictionary()
        bsdd_gui.on_new_project()
        
    @classmethod
    def load_project(cls,path:os.PathLike):
        prop = cls.get_properties()
        prop.project_dictionary = bsdd_parser.models.BsddDictionary.load(path)
        bsdd_gui.on_new_project()
        return prop.project_dictionary