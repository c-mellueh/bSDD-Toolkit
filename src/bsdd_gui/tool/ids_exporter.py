from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_json import BsddDictionary, BsddClass, BsddProperty, BsddClassProperty
import bsdd_gui
from ifctester.facet import Property as PropertyFacet
from ifctester.facet import Entity as EntityFacet

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
        for bsdd_class in sorted(bsdd_dict.Classes, key=lambda x: x.Code):
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
                spec.requirements += cls.build_property_requirements(class_prop, bsdd_dict)
            spec.requirements += cls.build_ifc_requirements(bsdd_class, bsdd_dict)
            ids.specifications.append(spec)
        ids.to_xml(out_path)
        print("EXPORT DONE!")

    @classmethod
    def build_property_requirements(cls, class_prop: BsddClassProperty, bsdd_dict: BsddDictionary):
        data_type = "IfcLabel"  # IfcLabel or IfcText

        bsdd_prop = prop_utils.get_property_by_class_property(class_prop)
        if bsdd_prop:
            uri = prop_utils.build_bsdd_uri(bsdd_prop, bsdd_dict)
        else:
            uri = None
        req = PropertyFacet(class_prop.PropertySet, prop_utils.get_name(class_prop))
        req.uri = uri
        req.cardinality = "optional"
        req.dataType = data_type
        values = prop_utils.get_values(class_prop)
        if values:
            req.value = Restriction({"enumeration": sorted([v.Value for v in values])})
        return [req]
    @classmethod
    def build_ifc_requirements(cls, bsdd_class: BsddClass, bsdd_dict: BsddDictionary):
        from bsdd_gui.tool.ifc_helper import IfcHelper

        classes = set()
        predefined_types = set()
        for ifc_reference in bsdd_class.RelatedIfcEntityNamesList:
            entity, predefined = IfcHelper.split_ifc_term(ifc_reference)
            classes.add(entity.upper())
            if predefined:
                predefined_types.add(predefined.upper())
            else:
                predefined_types.add("NOTDEFINED")
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
