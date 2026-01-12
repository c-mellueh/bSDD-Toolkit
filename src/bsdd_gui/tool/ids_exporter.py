from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict, Literal
import logging
from bsdd_json import BsddDictionary, BsddClass, BsddProperty, BsddClassProperty
import bsdd_gui
from ifctester.facet import Property as PropertyFacet
from ifctester.facet import Entity as EntityFacet

from ifctester.facet import Restriction
from ifctester.ids import Specification, Ids
from bsdd_gui.presets.signal_presets import FieldSignals, ViewSignals
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool, ItemViewTool
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import class_utils
from bsdd_gui.module.ids_exporter import ui, models, model_views, constants
from operator import itemgetter
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QDate, Signal, Qt, QObject, QThread
import datetime
from ifctester.facet import Classification as ClassificationFacet
from ifctester.facet import Property as PropertyFacet

if TYPE_CHECKING:
    from bsdd_gui.module.ids_exporter.prop import (
        IdsExporterProperties,
        IdsClassViewProperties,
        IdsPropertyViewProperties,
    )
from bsdd_gui.module.ids_exporter import trigger
import ifctester
import os
from bsdd_gui.presets.ui_presets import run_iterable_with_progress


class PsetDict(TypedDict):
    checked: bool
    proeprties: dict[str, bool]


class SettingsDict(TypedDict):
    class_settings: dict[str, bool]
    property_settings: dict[str, dict[str, PsetDict]]
    settings: BasicSettingsDict
    ids_metadata: MetadataDict


class BasicSettingsDict(TypedDict):
    inherit: bool
    classification: bool
    type_objects: bool
    main_pset: str
    main_property: str
    datatype: Literal["IfcLabel", "IfcText"]


class PayLoadDict(TypedDict):
    ids: Ids
    sorted_classes: list[BsddClass]
    base_settings: BasicSettingsDict
    class_settings: dict[str, bool]
    property_settings: dict[str, dict[str, PsetDict]]
    bsdd_dict: BsddDictionary
    ifc_version: list[str]
    out_path: str


class MetadataDict(TypedDict):
    title: str
    description: str
    author: str
    milestone: str
    purpose: str
    version: str
    copyright: str
    date: datetime.date
    ifc_versions: list[str]


class IdsSignals(FieldSignals):
    run_clicked = Signal(QWidget)


class IdsExporter(ActionTool, FieldTool):
    signals = IdsSignals()

    @classmethod
    def get_properties(cls) -> IdsExporterProperties:
        return bsdd_gui.IdsExporterProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.IdsWidget

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        # live sync of fields
        cls.signals.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.bsdd_data, f))

    @classmethod
    def connect_widget_signals(cls, widget: ui.IdsWidget):
        super().connect_widget_signals(widget)
        widget.cb_clsf.toggled.connect(lambda state: widget.widget_prop.setVisible(not state))
        widget.cb_pset.currentTextChanged.connect(lambda _: cls.fill_prop_combobox(widget))
        widget.cb_pset.currentIndexChanged.connect(lambda _: cls.fill_prop_combobox(widget))
        widget.pb_import.clicked.connect(lambda: trigger.import_settings(widget))
        widget.pb_export.clicked.connect(lambda: trigger.export_settings(widget))
        widget.pb_create.clicked.connect(lambda _, w=widget: trigger.export_ids(w))
        return widget

    @classmethod
    def get_template(cls):
        from bsdd_gui.resources.data import DATA_PATH
        from bsdd_gui import tool

        var = "ids_template"
        path = tool.Appdata.get_path(var)
        if not path:
            path = os.path.join(DATA_PATH, "template.ids")
        tool.Appdata.set_path(var, path)
        return path

    @classmethod
    def build_inherited_checkstate_dict(
        cls, bsdd_classes: list[BsddClass], old_checkstate_dict: dict[str, bool]
    ):
        def _iter_classes(child_classes: list[BsddClass], parent_checkstate: bool):
            for child in child_classes:
                checkstate = old_checkstate_dict.get(child.Code, True) and parent_checkstate
                new_checkstate_dict[child.Code] = checkstate
                _iter_classes(class_utils.get_children(child), checkstate)

        new_checkstate_dict: dict[str, bool] = dict()
        root_classes = [c for c in bsdd_classes if not c.ParentClassCode]
        _iter_classes(root_classes, True)
        return new_checkstate_dict

    @classmethod
    def is_class_active(
        cls, bsdd_class: BsddClass, class_settings: dict[str, bool], inherit_checkstates: bool
    ):
        checkstate = class_settings.get(bsdd_class.Code, True)
        if not inherit_checkstates or not checkstate:
            return checkstate
        parent = bsdd_class.ParentClassCode
        if not parent:
            return checkstate

    @classmethod
    def is_class_prop_active(cls, class_prop: BsddClassProperty, property_settings: PsetDict):
        pset_dict = property_settings.get(class_prop.PropertySet, dict())
        pset_checkstate = pset_dict.get("checked")
        if pset_checkstate is None:
            return True
        elif pset_checkstate is False:
            return False
        return pset_dict.get("properties", dict()).get(class_prop.Code, True)

    # Copyright (c) 2024 BIM-Tools
    # Licensed under the MIT License
    @classmethod
    def get_data_type(cls, dataType, propertyUri):
        if propertyUri in constants.PROPERTY_DATATYPE_MAPPING:
            return constants.PROPERTY_DATATYPE_MAPPING[propertyUri]
        return constants.DATATYPE_MAPPING.get(dataType, "IFCLABEL")

    # Copyright (c) 2024 BIM-Tools
    # Licensed under the MIT License
    @classmethod
    def add_property_facet(cls, bsdd_property: BsddClassProperty, bsdd_dictionary):

        value = None
        pattern = bsdd_property.Pattern
        allowed_values = bsdd_property.AllowedValues
        predefined_value = bsdd_property.PredefinedValue

        if pattern:
            value = Restriction(options={"pattern": pattern})
        elif allowed_values:
            value = Restriction(
                options={"enumeration": [x.Value for x in allowed_values if x.Value is not None]}
            )
        elif predefined_value:
            value = predefined_value

        property_facet = PropertyFacet(
            bsdd_property.PropertySet,
            prop_utils.get_name(bsdd_property, bsdd_dictionary),
            value,
            cls.get_data_type(
                prop_utils.get_data_type(bsdd_property), bsdd_property.PropertyUri
            ).upper(),
            bsdd_property.PropertyUri,
        )
        return property_facet

    @classmethod
    def build_ifc_requirements(
        cls, bsdd_class: BsddClass, bsdd_dict: BsddDictionary, add_type_objects: bool = False
    ):
        from bsdd_gui.tool.ifc_helper import IfcHelper

        def _get_type_class(class_name):
            for type_class in type_classes:
                if class_name in type_class:
                    return type_class.upper()
            return None

        type_classes = cls.get_properties().type_classes
        classes = set()
        predefined_types = set()
        for ifc_reference in bsdd_class.RelatedIfcEntityNamesList or []:
            entity, predefined = IfcHelper.split_ifc_term(ifc_reference)
            classes.add(entity.upper())
            predefined = predefined if predefined else "NOTDEFINED"
            predefined_types.add(predefined)
            if add_type_objects:
                type_class = _get_type_class(entity)
                if type_class:
                    classes.add(type_class)
        req = EntityFacet()
        class_res = Restriction({"enumeration": sorted(classes)})
        req.name = class_res
        if predefined_types and predefined_types != {"NOTDEFINED"}:
            pt_res = Restriction({"enumeration": sorted(predefined_types)})
            req.predefinedType = pt_res
        return [req]

    @classmethod
    def deprecated_build_ifc_requirements(cls, bsdd_class: BsddClass, bsdd_dict: BsddDictionary):
        """
        this doesn't work because the documentation and the xsd say different things:
        XSD:
            Contrary to other requirements facet extensions, cardinality is not available in the entityType facet when used for requirements.
            Its cardinality state is always considered to be "required".
        Docu allowes for optinal e.G.
            If applicable object is an IFCWINDOW entity, it must also have the SKYLIGHT predefined type.
        """
        from bsdd_gui.tool.ifc_helper import IfcHelper

        data_dict = dict()
        for ifc_reference in bsdd_class.RelatedIfcEntityNamesList:
            entity, predefined = IfcHelper.split_ifc_term(ifc_reference)
            if entity not in data_dict:
                data_dict[entity] = set()
            if predefined:
                data_dict[entity].add(predefined)

        req = EntityFacet()
        d = {"enumeration": sorted(data_dict.keys())}
        req.name = Restriction(d)
        req.cardinality = "required"
        requirements = [req]
        if all(len(pt) == 0 for en, pt in data_dict.items()):
            return requirements

        for entity_name, predefined_types in data_dict.items():
            if not predefined_types:
                continue
            req = EntityFacet(entity_name)
            req.predefinedType = Restriction({"enumeration": list(predefined_types)})
            req.cardinality = "optional"
            requirements.append(req)
        return requirements

    @classmethod
    def get_widget(cls, data) -> ui.IdsWidget:
        return super().get_widget(data)

    @classmethod
    def count_properties_with_progress(
        cls, parent: QWidget, classes: list["BsddClass"], inline_parent: QWidget | None = None
    ):
        """
        [Unverified] Wraps the outer loop in a worker thread with progress embedded in the UI.
        """

        # initialize once in the GUI thread
        count_dict: dict[str, dict] = {}
        cls.get_properties().property_count = count_dict

        def process_bsdd_class(bsdd_class: BsddClass, idx: int):
            # runs in worker thread – no UI calls here
            existing_psets: list[str] = []
            for class_prop in bsdd_class.ClassProperties:
                pset_name = class_prop.PropertySet
                prop_name = prop_utils.get_name(class_prop)
                if not prop_name:
                    continue
                if pset_name not in count_dict:
                    count_dict[pset_name] = {"properties": {}, "count": 0}

                if pset_name not in existing_psets:
                    count_dict[pset_name]["count"] += 1
                    existing_psets.append(pset_name)

                if prop_name not in count_dict[pset_name]["properties"]:
                    count_dict[pset_name]["properties"][prop_name] = 0

                count_dict[pset_name]["properties"][prop_name] += 1

        worker, thread, dialog = run_iterable_with_progress(
            parent=parent,
            iterable=classes,
            total=len(classes),
            title="Counting properties…",
            text="",
            cancel_text="Cancel",
            process_func=process_bsdd_class,
            inline_parent=inline_parent,
        )

        # keep references on the class or the caller side if needed
        return worker, thread, dialog

    @classmethod
    def fill_pset_combobox(cls, widget: ui.IdsWidget):
        count_dict = cls.get_properties().property_count
        pset_names = {pset: data["count"] for pset, data in count_dict.items()}
        widget.cb_pset.clear()
        if not pset_names:
            return
        # sort all psets by occurence count
        widget.cb_pset.addItems(sorted(pset_names, key=pset_names.get, reverse=True))
        widget.cb_pset.show()
        widget.cb_prop.show()

    @classmethod
    def fill_prop_combobox(cls, widget: ui.IdsWidget):
        pset_name = widget.cb_pset.currentText()
        count_dict = cls.get_properties().property_count
        count_dict = count_dict.get(pset_name, {})
        prop_names = count_dict.get("properties", {})
        widget.cb_prop.clear()
        if not prop_names:
            return
        widget.cb_prop.addItems(sorted(prop_names, key=prop_names.get, reverse=True))

    @classmethod
    def get_settings(cls, widget: ui.IdsWidget) -> BasicSettingsDict:
        settings_dict = {
            "inherit": widget.cb_inh.isChecked(),
            "classification": widget.cb_clsf.isChecked(),
            "type_objects": widget.cb_type_objects.isChecked(),
            "main_pset": widget.cb_pset.currentText(),
            "main_property": widget.cb_prop.currentText(),
            "datatype": widget.cb_datatype.currentText(),
        }
        return settings_dict

    @classmethod
    def get_ids_metadata(cls, widget: ui.IdsWidget) -> MetadataDict:
        metadata_dict = {
            "title": widget.le_title.text(),
            "description": widget.le_desc.text(),
            "author": widget.le_author.text(),
            "milestone": widget.le_miles.text(),
            "purpose": widget.le_purpose.text(),
            "version": widget.le_version.text(),
            "copyright": widget.le_copyr.text(),
            "date": widget.dt_date.dt_edit.date().toPython().strftime(r"%Y-%m-%d"),
            "ifc_versions": widget.ti_ifc_vers.tags(),
        }
        return metadata_dict

    @classmethod
    def set_ids_metadata(cls, widget: ui.IdsWidget, metadata: MetadataDict):
        widget.le_title.setText(metadata.get("title", ""))
        widget.le_desc.setText(metadata.get("description", ""))
        widget.le_author.setText(metadata.get("author", ""))
        widget.le_miles.setText(metadata.get("milestone", ""))
        widget.le_purpose.setText(metadata.get("purpose", ""))
        widget.le_version.setText(metadata.get("version", ""))
        widget.le_copyr.setText(metadata.get("copyright", ""))

        dt = metadata.get("date")
        if dt is not None:
            dt = datetime.datetime.strptime(dt, r"%Y-%m-%d")
            widget.dt_date.dt_edit.setDate(QDate(dt.year, dt.month, dt.day))

        ifc_versions = metadata.get("ifc_versions", ["IFC4X3_ADD2"])
        widget.ti_ifc_vers.setTags(ifc_versions)

    @classmethod
    def set_settings(cls, widget: ui.IdsWidget, settings_dict: dict):
        inherit = settings_dict.get("inherit")
        classification = settings_dict.get("classification")
        pset = settings_dict.get("main_pset")
        prop = settings_dict.get("main_property")

        if inherit is not None:
            widget.cb_inh.setChecked(inherit)
        if classification is not None:
            widget.cb_clsf.setChecked(classification)
        if pset is not None:
            widget.cb_pset.setCurrentText(pset)
        if prop is not None:
            widget.cb_prop.setCurrentText(prop)

    @classmethod
    def build_classification_facet(cls, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary):

        return ClassificationFacet(
            bsdd_class.Code,
            bsdd_dictionary.DictionaryName,
            uri=class_utils.build_bsdd_uri(bsdd_class, bsdd_dictionary),
            cardinality="optional",
        )

    @classmethod
    def build_main_property_facet(cls, bsdd_class: BsddClass, base_settings: BasicSettingsDict):
        return PropertyFacet(
            base_settings.get("main_pset"),
            base_settings.get("main_property"),
            bsdd_class.Code,
            base_settings.get("datatype"),
            cardinality="optional",
        )

    @classmethod
    def create_build_thread(
        cls,
        payload: PayLoadDict,
        parent: QWidget,
    ):
        """
        [Unverified] Wraps the outer loop in a worker thread with progress embedded in the UI.
        """

        def _process_bsdd_class(bsdd_class: BsddClass, idx: int):
            if not class_settings.get(bsdd_class.Code, True):
                return

            spec = Specification(
                f"Check for {bsdd_class.Code}",
                ifcVersion=ifc_version,
                identifier=bsdd_class.Code,
                description="Auto-generated from bSDD",
            )
            if base_settings.get("classification", False):
                applicability_facet = cls.build_classification_facet(bsdd_class, bsdd_dict)
            else:
                applicability_facet = cls.build_main_property_facet(bsdd_class, base_settings)
            spec.applicability.append(applicability_facet)
            for class_prop in bsdd_class.ClassProperties:
                if not cls.is_class_prop_active(
                    class_prop, property_settings.get(bsdd_class.Code, dict())
                ):
                    continue

                facet = cls.add_property_facet(class_prop, bsdd_dict)
                if facet:
                    spec.requirements.append(facet)

            spec.requirements += cls.build_ifc_requirements(
                bsdd_class, bsdd_dict, base_settings.get("type_objects", False)
            )
            ids.specifications.append(spec)

        # initialize once in the GUI thread
        ids = payload["ids"]
        sorted_classes = payload["sorted_classes"]
        base_settings = payload["base_settings"]
        class_settings = payload["class_settings"]
        property_settings = payload["property_settings"]
        bsdd_dict = payload["bsdd_dict"]
        ifc_version = payload["ifc_version"]

        count_dict: dict[str, dict] = {}
        cls.get_properties().property_count = count_dict

        worker, thread, dialog = run_iterable_with_progress(
            parent=parent,
            iterable=sorted_classes,
            total=len(sorted_classes),
            title="Create Specifications…",
            text="",
            cancel_text="Cancel",
            process_func=_process_bsdd_class,
            inline_parent=parent,
        )
        cls.get_properties().specification_worker = worker
        cls.get_properties().specification_thread = thread
        cls.get_properties().specification_widget = dialog
        # keep references on the class or the caller side if needed
        return worker, thread, dialog

    @classmethod
    def fill_ids_by_metadata(cls, ids, metadata: MetadataDict):

        ids.info["title"] = metadata.get("title", ids.info.get("title"))
        ids.info["description"] = metadata.get("description", ids.info.get("description"))
        ids.info["author"] = metadata.get("author", ids.info.get("author"))
        ids.info["milestone"] = metadata.get("milestone", ids.info.get("milestone"))
        ids.info["purpose"] = metadata.get("purpose", ids.info.get("purpose"))
        ids.info["version"] = metadata.get("version", ids.info.get("version"))
        ids.info["copyright"] = metadata.get("copyright", ids.info.get("copyright"))

    @classmethod
    def create_export_setup_thread(
        cls,
        widget: ui.IdsWidget,
        class_settings: dict[str, bool],
        property_settings: PsetDict,
        base_settings: BasicSettingsDict,
        metadata_settings: MetadataDict,
    ):
        class _SetupWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                    out_path = widget.fw_output.get_path()
                    template_path = cls.get_template()
                    ifc_version = metadata_settings.get("ifc_versions", ["IFC4X3_ADD2"])
                    bsdd_dict = widget.bsdd_data
                    ids = ifctester.ids.open(template_path)
                    base_spec = ids.specifications[0]
                    if base_settings.get("classification", False):
                        ids.specifications = list()
                    else:
                        base_requirement: PropertyFacet = base_spec.requirements[0]
                        base_requirement.propertySet = base_settings.get("main_pset", "")
                        base_requirement.baseName = base_settings.get("main_property", "")
                        base_restriction = base_requirement.value
                        base_restriction.options = {
                            "enumeration": [c.Code for c in bsdd_dict.Classes]
                        }
                        base_spec.ifcVersion = ifc_version

                    cls.fill_ids_by_metadata(ids, metadata_settings)
                    if base_settings["inherit"]:
                        cs = cls.build_inherited_checkstate_dict(bsdd_dict.Classes, class_settings)
                    else:
                        cs = class_settings

                    sorted_classes = sorted(bsdd_dict.Classes, key=lambda x: x.Code)
                    payload: PayLoadDict = {
                        "ids": ids,
                        "sorted_classes": sorted_classes,
                        "base_settings": base_settings,
                        "class_settings": cs,
                        "property_settings": property_settings,
                        "bsdd_dict": bsdd_dict,
                        "ifc_version": ifc_version,
                        "out_path": out_path,
                    }
                    self.finished.emit(payload)
                except Exception as exc:  # pragma: no cover - pass through
                    self.error.emit(exc)

        setup_worker = _SetupWorker()
        cls.get_properties().setup_worker = setup_worker
        setup_thread = QThread()

        cls.get_properties().setup_thread = setup_thread

        setup_worker.moveToThread(setup_thread)
        setup_worker.finished.connect(setup_thread.quit)
        setup_worker.finished.connect(setup_worker.deleteLater)
        setup_worker.error.connect(setup_thread.quit)
        setup_worker.error.connect(setup_worker.deleteLater)
        setup_thread.finished.connect(setup_thread.deleteLater)
        setup_thread.started.connect(setup_worker.run, Qt.ConnectionType.QueuedConnection)
        return setup_worker, setup_thread

    @classmethod
    def create_write_thread(cls, ids, out_path):
        class _SetupWorker(QObject):
            finished = Signal()
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                    ids.to_xml(out_path)
                    self.finished.emit()
                except Exception as exc:  # pragma: no cover - pass through
                    logging.error(exc)
                    self.error.emit(exc)

        write_worker = _SetupWorker()
        cls.get_properties().write_worker = write_worker
        write_thread = QThread()
        cls.get_properties().write_thread = write_thread
        write_worker.moveToThread(write_thread)
        write_worker.finished.connect(write_thread.quit)
        write_worker.finished.connect(write_worker.deleteLater)
        write_worker.error.connect(write_thread.quit)
        write_worker.error.connect(write_worker.deleteLater)
        write_thread.finished.connect(write_thread.deleteLater)
        write_thread.started.connect(write_worker.run, Qt.ConnectionType.QueuedConnection)
        return write_worker, write_thread


class ClassSignals(ViewSignals):
    pass


class IdsClassView(ItemViewTool):
    signals = ClassSignals()

    @classmethod
    def get_properties(cls) -> IdsClassViewProperties:
        return bsdd_gui.IdsClassViewProperties  #

    @classmethod
    def _get_model_class(cls):
        return models.ClassTreeModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_proxy_model_class(cls):
        return models.SortModel

    @classmethod
    def connect_settings_signals(cls, widget: ui.IdsWidget, view: model_views.ClassView):
        class_model = view.model().sourceModel()
        widget.cb_inh.toggled.connect(
            lambda checked: class_model.set_checkstate_inheritance(checked)
        )

        return super().connect_view_signals(view)

    @classmethod
    def get_checkstate(cls, bsdd_class: BsddClass):
        return cls.get_properties().checkstate_dict.get(bsdd_class.Code, True)

    @classmethod
    def set_checkstate(cls, bsdd_class: BsddClass, state: bool):
        cls.get_properties().checkstate_dict[bsdd_class.Code] = state

    @classmethod
    def get_check_dict(cls):
        return cls.get_properties().checkstate_dict

    @classmethod
    def set_check_dict(cls, check_dict, treev_view: model_views.ClassView):
        model: models.ClassTreeModel = treev_view.model().sourceModel()
        model.beginResetModel()
        cls.get_properties().checkstate_dict = check_dict
        model.endResetModel()


class PropertySignals(ViewSignals):
    pass


class IdsPropertyView(ItemViewTool):
    signals = PropertySignals()

    @classmethod
    def get_properties(cls) -> IdsPropertyViewProperties:
        return bsdd_gui.IdsPropertyViewProperties

    @classmethod
    def _get_model_class(cls):
        return models.PropertyTreeModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_proxy_model_class(cls):
        return models.SortModel

    @classmethod
    def _get_name(cls, bsdd_property: BsddClassProperty | str):
        if isinstance(bsdd_property, str):
            return bsdd_property
        return prop_utils.get_name(bsdd_property)

    @classmethod
    def _get_code(cls, bsdd_property: BsddClassProperty | str):
        if isinstance(bsdd_property, str):
            return ""
        return bsdd_property.Code

    @classmethod
    def get_checkstate(
        cls, model: models.PropertyTreeModel, bsdd_class_property: BsddClassProperty | str
    ):
        pset_name = (
            bsdd_class_property
            if isinstance(bsdd_class_property, str)
            else bsdd_class_property.PropertySet
        )
        property_code = None if isinstance(bsdd_class_property, str) else bsdd_class_property.Code
        bsdd_class_code = model.bsdd_data.Code
        checkstate_dict: PsetDict = cls.get_properties().checkstate_dict
        class_dict = checkstate_dict.get(bsdd_class_code, None)
        if not class_dict:
            return True
        pset_dict = class_dict.get(pset_name)
        if not pset_dict:
            return True
        if property_code is None:  # propertySet
            return pset_dict.get("checked", True)
        else:
            return pset_dict["properties"].get(property_code, True)

    @classmethod
    def set_checkstate(
        cls,
        model: models.PropertyTreeModel,
        bsdd_class: BsddClass,
        bsdd_class_property: BsddClassProperty | str,
        state: bool,
    ):
        if not model.bsdd_data:
            return

        pset_name = (
            bsdd_class_property
            if isinstance(bsdd_class_property, str)
            else bsdd_class_property.PropertySet
        )
        property_code = None if isinstance(bsdd_class_property, str) else bsdd_class_property.Code
        if bsdd_class.Code not in cls.get_properties().checkstate_dict:
            cls.get_properties().checkstate_dict[bsdd_class.Code] = dict()
        checkstate_dict = cls.get_properties().checkstate_dict[bsdd_class.Code]
        if not pset_name in checkstate_dict:
            checkstate_dict[pset_name] = {"checked": True, "properties": dict()}
        if not property_code:
            checkstate_dict[pset_name]["checked"] = state
        else:
            checkstate_dict[pset_name]["properties"][property_code] = state

    @classmethod
    def get_check_dict(cls):
        return cls.get_properties().checkstate_dict

    @classmethod
    def set_check_dict(cls, check_dict, tree_view: model_views.PropertyView):
        model: models.ClassTreeModel = tree_view.model().sourceModel()
        model.beginResetModel()
        cls.get_properties().checkstate_dict = check_dict
        model.endResetModel()
