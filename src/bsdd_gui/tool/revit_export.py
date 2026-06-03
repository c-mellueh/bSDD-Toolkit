from __future__ import annotations
from typing import TYPE_CHECKING,Literal
from PySide6.QtCore import Signal, QObject, QThread, Qt
from bsdd_json.utils import property_utils
from pathlib import Path
from jinja2 import Template

import logging
from bsdd_json import BsddDictionary, BsddProperty
import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool, FieldSignals
from bsdd_gui.module.revit_export import ui, trigger
from bsdd_gui.resources.data import get_shared_parameter_template_path
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from bsdd_gui.module.revit_export.prop import RevitExportProperties
    from bsdd_gui.tool.loin import CheckstateDict


Mode = Literal["CustomPropertySet", "SharedParameters"]

class Signals(FieldSignals):
    pass


class RevitExport(ActionTool, FieldTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> RevitExportProperties:
        return bsdd_gui.RevitExportProperties

    @classmethod
    def _get_widget_class(cls) -> type[ui.Widget]:
        return ui.Widget

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
        widget.cb_mode.currentIndexChanged.connect(lambda _,w=widget: cls.sync_settings_layout(w))
        widget.cb_mode.currentIndexChanged.connect(lambda _,w=widget: cls.sync_settings_to_properties(w))
        widget.cb_text.currentIndexChanged.connect(lambda _,w=widget: cls.sync_settings_to_properties(w))
        super().connect_widget_signals(widget)


    @classmethod
    def sync_settings_layout(cls,widget:ui.Widget):
        mode = widget.cb_mode
        widget.cb_text.setVisible(mode.currentText() == "CustomPropertySet")
        widget.lb_text_or_label.setVisible(mode.currentText() == "CustomPropertySet")


    @classmethod
    def sync_settings_to_properties(cls,widget:ui.Widget):
        cls.get_properties().text_or_label = widget.cb_text.currentText()
        cls.get_properties().mode = widget.cb_mode.currentText()

    @classmethod
    def get_mode(cls) -> Mode:
        return cls.get_properties().mode

    @classmethod
    def get_datatype(cls,bsdd_property:BsddProperty,mode:Mode = "CustomPropertySet") -> str:

        datatype_mapping = {
            "Boolean":"Boolean",
            "Character":"Label",
            "Integer":"Integer",
            "Real":"Real",
            "String":cls.get_properties().text_or_label,
            "Time":"Time"
    } if mode == "CustomPropertySet" else {
            "Boolean":"YESNO",
            "Character":"TEXT",
            "Integer":"INTEGER",
            "Real":"NUMBER",
            "String":"TEXT",
            "Time":"TIMEINTERVAL"
    }
        default = cls.get_properties().text_or_label if mode == "CustomPropertySet" else "TEXT"
        return datatype_mapping.get(bsdd_property.DataType,default)

    @classmethod
    def get_revit_name(cls,pset_name:str,bsdd_property:BsddProperty):
        #TODO: Extend to allow different possibilities like only the Property name without the pset name, other seperators etc
        return  f"{pset_name}.{bsdd_property.Name}"

    @classmethod
    def get_property_name(cls,bsdd_property:BsddProperty):
        #TODO: Extend to allow other property names, e.g. The Property Code or with a prefix:
        return bsdd_property.Name

    @classmethod
    def get_template_path(cls) -> Path:
        #TODO: Add settings menu to set custom template Path
        return  get_shared_parameter_template_path()


    @classmethod
    def create_line(cls,pset_name:str,bsdd_property:BsddProperty):
        revit_name = cls.get_revit_name(pset_name,bsdd_property)
        datatype = cls.get_datatype(bsdd_property,mode = "CustomPropertySet")
        name = cls.get_property_name(bsdd_property)
        return "\t".join([name,datatype,revit_name])


    @classmethod
    def get_ifc_types(cls,checkstates:CheckstateDict,pset_name:str):
        ifc_types:set[str] = set()
        for _,class_dict in checkstates.items():
            bsdd_class = class_dict["bsdd_entity"]
            if pset_dict:= class_dict["property_sets"].get(pset_name):
                if not pset_dict["checked"]:
                    continue
                ifc_types.update(set(bsdd_class.RelatedIfcEntityNamesList or[]))
        return ifc_types

    @classmethod
    def create_userdefined_psets(cls,checkstates:CheckstateDict,psets:dict[str,set[str]],bsdd_dictionary:BsddDictionary):
        lines = list()
        for pset_name,class_property_codes in psets.items():
            ifc_types = sorted(cls.get_ifc_types(checkstates,pset_name))
            text = "\t".join(["PropertySet:",pset_name,"I",",".join(ifc_types)])
            property_texts = list()
            for class_property_code in class_property_codes:
                logger.debug(f"Search for {pset_name}.{class_property_code}")
                bsdd_property = cls.get_properties_by_codes(pset_name,class_property_code,bsdd_dictionary,checkstates)
                if not bsdd_property:
                    logger.warning(f"bSDD Property '{pset_name}.{class_property_code}' konnte nicht gefunden werden")
                    continue
                logger.debug(f"Ppoperty Found: {bsdd_property.Code}")
                line = cls.create_line(pset_name,bsdd_property)
                property_texts.append(line)
                logger.debug(f"Line Created:\n\t {line}")

            if not property_texts:
                continue
            
            lines.append(f"{text}")
            lines+=property_texts
            lines.append("")
        return lines

    @classmethod
    def get_properties_by_codes(cls,pset_name:str,class_property_code:str,bsdd_dictionary:BsddDictionary,checkstates:CheckstateDict) -> BsddProperty:
        predefined_psets = {pset.Name:pset for pset in bsdd_dictionary.Classes if pset.ClassType == "GroupOfProperties"}
        if pset_class:= predefined_psets.get(pset_name):
            if class_property:={cp.Code:cp for cp in pset_class.ClassProperties}.get(class_property_code):
                return property_utils.get_property_by_class_property(class_property,bsdd_dictionary)
        #Fallback if no predefined PSet is created
        #Search all Classes and find a checked property with correct pset
        else:
            for _,class_dict in checkstates.items():
                if not class_dict.get("checked",False):
                    continue
                for pset_name_key,pset_dict in class_dict["property_sets"].items():
                    if not pset_dict.get("checked"):
                        continue

                    if pset_name != pset_name_key:
                        continue
                    for property_code_key,property_dict in pset_dict["properties"].items():
                        if property_code_key == class_property_code:
                            if bsdd_property:= property_dict.get("bsdd_property"):
                                return bsdd_property
        return None
    
    @classmethod
    def create_shared_parameters(cls,checkstates:CheckstateDict,psets:dict[str,set[str]],bsdd_dictionary:BsddDictionary):
        template_path = cls.get_template_path()
        lines = list()
        groups = ["SOM"]
        for pset_name,class_property_codes in psets.items():
            for class_property_code in class_property_codes:
                bsdd_property = cls.get_properties_by_codes(pset_name,class_property_code,bsdd_dictionary,checkstates)
                if not bsdd_property:
                    logger.warning(f"bSDD Property '{pset_name}.{class_property_code}' konnte nicht gefunden werden")
                    continue
                uid = property_utils.get_uid(bsdd_property)
                name = cls.get_revit_name(pset_name,bsdd_property)
                datatype = cls.get_datatype(bsdd_property,mode = "SharedParameters")
                datacategory = ""
                group_index = 1
                visible = 1
                description = bsdd_property.Definition
                usermodifiable = 0
                hide_when_no_value = 0
                lines.append((uid,name,datatype,datacategory,group_index,visible,description,usermodifiable,hide_when_no_value))
        result = Template(open(template_path).read()).render(groups = groups,params = lines)
        return result, lines
    
    @classmethod
    def create_userdefined_pset_thread(
        cls,
        bsdd_dict: BsddDictionary,
        checkstate_dict:CheckstateDict,
        pset_dict:dict[str,dict[str,bool]],
        out_path: str,
    ):
        class _BuildWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                    logging.info("Start Export!")

                    lines = cls.create_userdefined_psets(checkstate_dict,pset_dict,bsdd_dict)
                    with open(out_path,"w") as file:
                        file.write("\n".join(lines))
                    logging.info("Export Done!")
                    self.finished.emit(lines)
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

    @classmethod
    def create_shared_paramaters_thread(
        cls,
        bsdd_dict: BsddDictionary,
        checkstate_dict:CheckstateDict,
        pset_dict:dict[str,dict[str,bool]],
        out_path: str,
    ):
        class _BuildWorker(QObject):
            finished = Signal(object)
            error = Signal(object)

            def __init__(self):
                super().__init__()

            def run(self):
                try:
                    logging.info("Start Export!")
                    text,lines = cls.create_shared_parameters(checkstate_dict,pset_dict,bsdd_dict)
                    with open(out_path,"w",encoding="utf-16") as file:
                        file.write(text)
                    logging.info("Export Done!")
                    self.finished.emit(lines)
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
