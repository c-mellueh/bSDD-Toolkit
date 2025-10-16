from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_json import BsddDictionary, BsddClass, BsddProperty
import bsdd_gui
from ifctester.facet import Property as PropertyFacet
from ifctester.facet import Restriction
from ifctester.ids import Specification

from bsdd_gui.presets.tool_presets import ActionTool
from bsdd_json.utils import property_utils as prop_utils

if TYPE_CHECKING:
    from bsdd_gui.module.ids_exporter.prop import IdsExporterProperties
from bsdd_gui.module.ids_exporter import trigger
import ifctester
import os


class IdsExporter(ActionTool):
    @classmethod
    def get_properties(cls) -> IdsExporterProperties:
        return bsdd_gui.IdsExporterProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def get_template(cls):
        from bsdd_gui.resources.data import DATA_PATH

        return ifctester.ids.open(os.path.join(DATA_PATH, "template.ids"))

    @classmethod
    def build_ids(cls, bsdd_dict: BsddDictionary):
        out_path = "test.ids"
        pset = "Allgemein"
        prop = "Klassifikation"
        data_type = "IfcLabel"  # IfcLabel or IfcText
        ifc_versions = [
            "IFC4X3_ADD2",
        ]
        ids = cls.get_template()
        base_spec = ids.specifications[0]
        base_requirement: PropertyFacet = base_spec.requirements[0]
        base_requirement.propertySet = pset
        base_requirement.baseName = prop
        base_restriction = base_requirement.value
        base_restriction.options = {"enumeration": [c.Code for c in bsdd_dict.Classes]}
        for bsdd_class in sorted(bsdd_dict.Classes,key=lambda x: x.Code):
            spec = Specification(
                f"Check for {bsdd_class.Code}",
                ifcVersion=ifc_versions,
                identifier=bsdd_class.Code,
                description="Auto-generated from bSDD",
            )
            applicability_facet = PropertyFacet(
                pset, prop, bsdd_class.Code, data_type, cardinality="optional"
            )
            spec.applicability.append(applicability_facet)
            for class_prop in bsdd_class.ClassProperties:
                req = PropertyFacet(class_prop.PropertySet, prop_utils.get_name(class_prop))
                req.cardinality = "optional"
                req.dataType = data_type
                values = prop_utils.get_values(class_prop)
                if values:
                    req.value = Restriction({"enumeration": sorted([v.Value for v in values])})
                spec.requirements.append(req)
            ids.specifications.append(spec)
        ids.to_xml(out_path)
