from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict
import logging
from PySide6.QtCore import Signal, QCoreApplication,QObject,QThread,Qt
from openpyxl import styles
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from bsdd_json.utils import class_utils, property_utils, dictionary_utils
from openpyxl.utils import get_column_letter
import openpyxl

from bsdd_json import BsddClass, BsddDictionary, BsddClassProperty,BsddProperty
import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool, FieldSignals
from bsdd_gui.module.iso_export import ui, trigger,constants
from openpyxl.worksheet.table import Table, TableStyleInfo
from uuid import uuid4
from datetime import datetime

from bsdd_gui.module.iso_export.datamodel import (
    NameInLanguage,
    PropertyGroup,
    Language,
    DefinitionInLanguage,
    Property,
    PhysicalQuantity,
    Container
)


class PsetDict(TypedDict):
    checked: bool
    properties: dict[str, bool]


class BasicSettingsDict(TypedDict):
    inherit: bool
    classification: bool
    type_objects: bool
    main_pset: str
    main_property: str


class SettingsDict(TypedDict):
    class_settings: dict[str, bool]
    property_settings: dict[str, dict[str, PsetDict]]
    settings: BasicSettingsDict


if TYPE_CHECKING:
    from bsdd_gui.module.iso_export.prop import IsoExportProperties


class Signals(FieldSignals):
    pass


class IsoExport(ActionTool, FieldTool):
    signals = Signals()
    @classmethod
    def get_properties(cls) -> IsoExportProperties:
        return bsdd_gui.IsoExportProperties

    @classmethod
    def _get_widget_class(cls) -> type[ui.Widget]:
        return ui.Widget

    @classmethod
    def request_widget(cls, *args, **kwargs):
        return super().request_widget(*args, **kwargs)

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def create_widget(cls, *args, **kwargs) -> ui.Widget:
        widget = cls._get_widget_class()(*args, **kwargs)
        cls.add_plugins_to_widget(widget)
        return widget

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.Widget):
        widget.pb_import.clicked.connect(lambda: trigger.import_settings(widget))
        widget.pb_export.clicked.connect(lambda: trigger.export_settings(widget))
        widget.pb_create.clicked.connect(lambda _, w=widget: trigger.export(w))
        super().connect_widget_signals(widget)


    @classmethod
    def get_settings(cls, widget: ui.Widget) -> BasicSettingsDict:

        settings_dict = {
        }
        return settings_dict

    @classmethod
    def set_settings(cls, widget: ui.Widget, settings_dict: BasicSettingsDict):
        pass

    @classmethod
    def create_class(cls,bsdd_class: BsddClass,mode: constants.MODE):
        guid = uuid4()
        status = (
            bsdd_class.Status.lower()
            if bsdd_class.Status != "Preview" and bsdd_class.Status
            else "active"
        )
        language = cls.get_properties().language
        country = cls.get_properties().country

        definition = DefinitionInLanguage(
            definition=bsdd_class.Definition or "undefined", language=language
        )
        name = NameInLanguage(name=bsdd_class.Name, language=language)
        countries_of_use = [x for x in bsdd_class.CountriesOfUse or [] ] or [country]
        item = PropertyGroup(
            guid=guid,
            status=status,
            dateOfCreation=datetime.now(),
            dateOfRevision=datetime.now(),
            dateOfVersion=datetime.now(),
            versionNumber=bsdd_class.VersionNumber or 1,
            revisionNumber=bsdd_class.RevisionNumber or 1,
            replaces=[],
            replacedBy=[],
            creatorsLanguage=language,
            namesInLanguage=[name],
            definitionsInLanguage=[definition],
            visualRepresentation=[bsdd_class.VisualRepresentationUri]
            if bsdd_class.VisualRepresentationUri
            else [],
            countryOfUse=countries_of_use,
            countryOfOrigin=bsdd_class.CountryOfOrigin or country,
            categoryOfGroupOfProperties=mode,
        )
        return guid, item

    @classmethod
    def create_property(cls,bsdd_class_property: BsddClassProperty, parent_guid: str,project:BsddDictionary):
        language = cls.get_properties().language
        bsdd_property = property_utils.get_property_by_class_property(
            bsdd_class_property, project
        )
        guid = uuid4()
        status = (
            bsdd_property.Status.lower()
            if bsdd_property.Status != "Preview" and bsdd_property.Status
            else "active"
        )
        name = NameInLanguage(name=bsdd_property.Name, language=language)
        definition = DefinitionInLanguage(definition=
            property_utils.get_definition(bsdd_class_property, project) or "undefined", language = language
        )
        prop = Property(
            guid=guid,
            status=status,
            dateOfCreation=datetime.now(),
            dateOfRevision=datetime.now(),
            dateOfVersion=datetime.now(),
            versionNumber=bsdd_property.VersionNumber or 1,
            revisionNumber=bsdd_property.RevisionNumber or 1,
            creatorsLanguage=language,
            namesInLanguage=[name],
            definitionsInLanguage=[definition],
            groupOfProperties=[parent_guid],
            countryOfUse=["DE"],
            physicalQuantity=[PhysicalQuantity(siUnit="without", language=language)],
            dataType=bsdd_property.DataType.upper(),
            dynamicProperty="no",
        )
        return bsdd_property, prop

    @classmethod
    def build_property_groups(cls,project:BsddDictionary):
        class_names = [c.Name for c in project.Classes if c.ClassType == "Class"]


        for pset in project.Classes:
            if pset.ClassType != "GroupOfProperties":
                continue
            if pset.Name in class_names:
                continue
            guid, xml_class = cls.create_class(pset,"name property set")
            cls.get_properties().property_groups[pset.Code] = {"guid": guid, "xml_pset": xml_class, "properties": {}}
            for pset_property in pset.ClassProperties:
                bsdd_property, xml_property = cls.create_property(pset_property, guid,project)
                if bsdd_property.Code not in cls.get_properties().bsdd_properties:
                    cls.get_properties().bsdd_properties[bsdd_property.Code] = xml_property
                cls.get_properties().property_groups[pset.Code]["properties"][bsdd_property.Code] = xml_property

    @classmethod
    def build_xml_properties(cls,project:BsddDictionary):
        for bsdd_class in project.Classes:
            if bsdd_class.ClassType != "Class":
                continue
            parent_class = class_utils.get_parent(bsdd_class,project)
            if parent_class:
                parent_prop_codes = [cl_prop.PropertyCode for cl_prop in parent_class.ClassProperties]
            else:
                parent_prop_codes = []

            guid, xml_class = cls.create_class(bsdd_class,"class")
            cls.get_properties().property_groups[bsdd_class.Code] = {"guid": guid, "xml_pset": xml_class, "properties": {}}
            for class_property in bsdd_class.ClassProperties:
                if class_property.PropertyCode in parent_prop_codes:
                    continue
                bsdd_property = property_utils.get_property_by_class_property(class_property,project)
                xml_property = cls.get_properties().bsdd_properties.get(bsdd_property.Code)
                if xml_property is None:
                    _,xml_property = cls.create_property(class_property,guid,project)
                    cls.get_properties().bsdd_properties[bsdd_property.Code] = xml_property
                    cls.get_properties().property_groups[bsdd_class.Code]["properties"][bsdd_property.Code] = xml_property
                else:
                    xml_property.groupOfProperties.append(guid)

    @classmethod
    def create_build_thread(
        cls,
        project: BsddDictionary,
        class_settings: dict[str, bool],
        property_settings: PsetDict,
        out_path:str
    ):
        class _BuildWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                    cls.get_properties().property_groups = {}
                    cls.get_properties().bsdd_properties:dict[BsddProperty,Property] = {}
                    cls.build_property_groups(project)
                    cls.build_xml_properties(project)
                    
                    pg  = cls.get_properties().property_groups
                    bp = cls.get_properties().bsdd_properties
                    v1 = [x["xml_pset"] for x in pg.values()]
                    v2 = list(bp.values())

                    for bsdd_class in project.Classes:
                        if not bsdd_class.ParentClassCode:
                            continue
                        xml_class:PropertyGroup = pg.get(bsdd_class.Code,{}).get("xml_pset")
                        parent_xml_pset:PropertyGroup = pg.get(bsdd_class.ParentClassCode,{}).get("xml_pset")
                        xml_class.parentGroupOfProperties = parent_xml_pset.guid

                    container = Container(propertyGroup=v1,property_=v2)
                    xml_bytes = container.to_xml(
                        encoding="UTF-8",
                        xml_declaration=True,
                        exclude_none=True,
                        exclude_unset=True,
                    )
                    with open(out_path, "wb") as f:
                        f.write(xml_bytes)

                    self.finished.emit(project.Classes)
                except Exception as exc:  # pragma: no cover - pass through
                    self.error.emit(exc)

        build_worker = _BuildWorker()
        cls.get_properties().build_worker = build_worker
        build_thread = QThread()

        cls.get_properties().build_thread = build_thread

        build_worker.moveToThread(build_thread)
        build_worker.finished.connect(build_thread.quit)
        build_worker.finished.connect(build_worker.deleteLater)
        build_worker.error.connect(build_thread.quit)
        build_worker.error.connect(build_worker.deleteLater)
        build_thread.finished.connect(build_thread.deleteLater)
        build_thread.started.connect(build_worker.run, Qt.ConnectionType.QueuedConnection)
        return build_worker, build_thread