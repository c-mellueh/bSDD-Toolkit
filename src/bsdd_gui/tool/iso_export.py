from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict
from PySide6.QtCore import Signal, QObject, QThread, Qt
from bsdd_json.utils import class_utils, property_utils

from bsdd_json import BsddClass, BsddDictionary, BsddClassProperty
import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool, FieldSignals
from bsdd_gui.module.iso_export import ui, trigger, constants
from uuid import UUID, uuid4
from datetime import datetime

from bsdd_gui.module.iso_export.datamodel import (
    NameInLanguage,
    PropertyGroup,
    DefinitionInLanguage,
    Property,
    PhysicalQuantity,
    Container,
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
        widget.pb_create.clicked.connect(lambda _, w=widget: trigger.export(w))
        super().connect_widget_signals(widget)

    # ------------------------------------------------------------------ format

    @classmethod
    def get_export_format(cls, widget: ui.Widget) -> str:
        """Return the currently-selected output format constant."""
        combo = getattr(widget, "cb_format", None)
        if combo is None:
            return constants.FORMAT_ISO_23386
        return combo.currentData() or constants.FORMAT_ISO_23386

    @classmethod
    def set_export_format(cls, widget: ui.Widget, value: str) -> None:
        combo = getattr(widget, "cb_format", None)
        if combo is None:
            return
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    @classmethod
    def create_class(cls, bsdd_class: BsddClass, mode: constants.MODE):
        if bsdd_class.ReferenceCode:
            guid = (
                UUID(bsdd_class.Uid)
                if isinstance(bsdd_class.Uid, str)
                else bsdd_class.Uid or uuid4()
            )
        else:
            guid = uuid4()
        bsdd_class.Uid = str(guid)

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
        countries_of_use = [x for x in bsdd_class.CountriesOfUse or []] or [country]
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
    def create_property(
        cls, bsdd_class_property: BsddClassProperty, parent_guid: str, project: BsddDictionary
    ):
        language = cls.get_properties().language
        bsdd_property = property_utils.get_property_by_class_property(bsdd_class_property, project)
        if bsdd_property.Uid:
            guid = (
                UUID(bsdd_property.Uid) if isinstance(bsdd_property.Uid, str) else bsdd_property.Uid
            )
        else:
            guid = uuid4()
        bsdd_property.Uid = str(guid)
        status = (
            bsdd_property.Status.lower()
            if bsdd_property.Status != "Preview" and bsdd_property.Status
            else "active"
        )
        name = NameInLanguage(name=bsdd_property.Name, language=language)
        definition = DefinitionInLanguage(
            definition=property_utils.get_definition(bsdd_class_property, project) or "undefined",
            language=language,
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
    def build_group_of_properties(
        cls, checked_predefined_properties: dict[str, dict[str, bool]], project: BsddDictionary
    ):
        """Build name property sets based on predefined proeprty sets (Classes that are typed as GroupOfProperties in bSDD)"""
        predefined_psets = {
            p.name: p for p in project.Classes if p.ClassType == "GroupOfProperties"
        }
        for pset_name, property_code_dict in checked_predefined_properties.items():
            pset = predefined_psets.get(pset_name)
            if pset is None:
                continue
            allowed_properties: list[BsddClassProperty] = [
                cp for cp in pset.ClassProperties if cp.Code in property_code_dict
            ]
            guid, xml_class = cls.create_class(pset, "name property set")
            cls.get_properties().property_groups[pset.Code] = {
                "guid": guid,
                "xml_pset": xml_class,
                "properties": {},
                "bsdd_class": pset,
            }
            for pset_property in allowed_properties:
                bsdd_property, xml_property = cls.create_property(pset_property, guid, project)
                if bsdd_property.Code not in cls.get_properties().bsdd_properties:
                    cls.get_properties().bsdd_properties[bsdd_property.Code] = xml_property
                cls.get_properties().property_groups[pset.Code]["properties"][
                    bsdd_property.Code
                ] = xml_property

    @classmethod
    def build_xml_properties(
        cls, project: BsddDictionary, checked_classes: list[BsddClass], checked_properties: dict
    ):
        for bsdd_class in checked_classes:
            if bsdd_class.ClassType != "Class":
                continue
            guid, xml_class = cls.create_class(bsdd_class, "class")
            cls.get_properties().property_groups[bsdd_class.Code] = {
                "guid": guid,
                "xml_pset": xml_class,
                "properties": {},
                "bsdd_class": bsdd_class,
            }
            for class_property in bsdd_class.ClassProperties:
                is_active = (
                    checked_properties.get(bsdd_class.Code, {})
                    .get(class_property.PropertySet, {})
                    .get(class_property.Code, True)
                )
                if not is_active:
                    continue
                bsdd_property = property_utils.get_property_by_class_property(
                    class_property, project
                )
                xml_property = cls.get_properties().bsdd_properties.get(bsdd_property.Code)
                if xml_property is None:
                    _, xml_property = cls.create_property(class_property, guid, project)
                    cls.get_properties().bsdd_properties[bsdd_property.Code] = xml_property
                    cls.get_properties().property_groups[bsdd_class.Code]["properties"][
                        bsdd_property.Code
                    ] = xml_property

                xml_property.groupOfProperties.append(guid)

    @classmethod
    def remove_inherited_properties(cls, project: BsddDictionary):

        def _is_parent(child: BsddClass, parent: BsddClass) -> bool:
            while parent is not None:
                if child == parent:
                    return True
                parent = class_utils.get_parent(parent, project, class_dict)
            return False

        property_groups = cls.get_properties().property_groups
        bsdd_properties = cls.get_properties().bsdd_properties

        class_dict = {c.Code: c for c in project.Classes}
        # property_groups is keyed by Code; build a guid→group reverse map for groupOfProperties lookup
        guid_to_group = {v["guid"]: v for v in property_groups.values()}
        for bsdd_property, xml_property in bsdd_properties.items():
            if len(xml_property.groupOfProperties) <= 1:
                continue
            parent_groups = xml_property.groupOfProperties.copy()
            for group_guid in parent_groups:
                xml_property_group = guid_to_group.get(group_guid)

                if xml_property_group is None:
                    continue
                bsdd_class = xml_property_group["bsdd_class"]
                for other_group_guid in parent_groups:
                    if group_guid == other_group_guid:
                        continue
                    other_xml_property_group = guid_to_group.get(other_group_guid)
                    if other_xml_property_group is None:
                        continue
                    other_bsdd_class = other_xml_property_group["bsdd_class"]
                    if _is_parent(bsdd_class, other_bsdd_class):
                        if group_guid in xml_property.groupOfProperties:
                            xml_property.groupOfProperties.remove(group_guid)

    @classmethod
    def build_parent_class_codes(cls, project: BsddDictionary, checked_classes: list[BsddClass]):
        """Set parentGroupOfProperties for all property groups based on the class hierarchy."""
        property_groups = cls.get_properties().property_groups
        for bsdd_class in project.Classes:
            if bsdd_class not in checked_classes:
                continue
            if not bsdd_class.ParentClassCode:
                continue
            parent = class_utils.get_parent(bsdd_class, project)
            if parent is None or parent not in checked_classes:
                continue
            xml_class: PropertyGroup = property_groups.get(bsdd_class.Code, {}).get("xml_pset")
            parent_xml_pset: PropertyGroup = property_groups.get(
                bsdd_class.ParentClassCode, {}
            ).get("xml_pset")
            xml_class.parentGroupOfProperties = parent_xml_pset.guid

    @classmethod
    def reset_data(cls):
        cls.get_properties().property_groups = {}
        cls.get_properties().bsdd_properties = {}

    @classmethod
    def build_container(cls):
        pg = cls.get_properties().property_groups
        bp = cls.get_properties().bsdd_properties
        container = Container(
            propertyGroup=[x["xml_pset"] for x in pg.values()], property_=list(bp.values())
        )
        return container

    @classmethod
    def _run_export(
        cls,
        project: BsddDictionary,
        checked_classes: dict[str, bool],
        checked_properties: PsetDict,
        checked_predefined_properties: dict[str, dict[str, bool]],
        out_path: str,
    ):
        cls.reset_data()
        cls.build_group_of_properties(checked_predefined_properties, project)
        cls.build_xml_properties(project, checked_classes, checked_properties)
        cls.build_parent_class_codes(project, checked_classes)
        cls.remove_inherited_properties(project)

        container = cls.build_container()
        xml_bytes = container.to_xml(
            encoding="UTF-8",
            xml_declaration=True,
            exclude_none=True,
            exclude_unset=True,
        )
        with open(out_path, "wb") as f:
            f.write(xml_bytes)

    @classmethod
    def create_build_thread(
        cls,
        project: BsddDictionary,
        checked_classes: dict[str, bool],
        checked_properties: PsetDict,
        checked_predefined_properties: dict[str, dict[str, bool]],
        out_path: str,
    ):
        class _BuildWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                    cls._run_export(
                        project,
                        checked_classes,
                        checked_properties,
                        checked_predefined_properties,
                        out_path,
                    )
                    self.finished.emit(len(cls.get_properties().property_groups))

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

    # ------------------------------------------------------------------ LOIN export

    @classmethod
    def create_loin_build_thread(cls, out_path: str):
        """Build a background thread that writes the in-memory LOIN to *out_path*."""

        class _LoinWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def run(self):
                try:
                    from bsdd_gui.tool.loin import Loin

                    count = Loin.export_to_xml(out_path)
                    self.finished.emit(count)
                except Exception as exc:  # pragma: no cover - pass through
                    self.error.emit(exc)

        worker = _LoinWorker()
        thread = QThread()
        cls.get_properties().build_worker = worker
        cls.get_properties().build_thread = thread

        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(thread.quit)
        worker.error.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.started.connect(worker.run, Qt.ConnectionType.QueuedConnection)
        return worker, thread
