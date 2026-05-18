"""
Tests for the IfcHelper module (tool/ifc_helper.py).

Covers split_ifc_term which uses a regex to separate the IFC entity name
from an optional predefined type suffix.
"""

from __future__ import annotations

from bsdd_gui.tool import IfcHelper


class TestSplitIfcTerm:
    def test_plain_entity_no_predefined_type(self):
        entity, predefined = IfcHelper.split_ifc_term("IfcWall")
        assert entity == "IfcWall"
        assert predefined is None

    def test_entity_with_all_caps_predefined_type(self):
        entity, predefined = IfcHelper.split_ifc_term("IfcElectricMotorSYNCHRONOUS")
        assert entity == "IfcElectricMotor"
        assert predefined == "SYNCHRONOUS"

    def test_entity_with_underscore_predefined_type(self):
        entity, predefined = IfcHelper.split_ifc_term("IfcWallSTANDARD_CASE")
        assert entity == "IfcWall"
        assert predefined == "STANDARD_CASE"

    def test_entity_with_single_char_predefined(self):
        entity, predefined = IfcHelper.split_ifc_term("IfcBeamT")
        # 'T' is uppercase so group 2 captures it
        assert entity == "IfcBeam"
        assert predefined == "T"

    def test_short_ifc_entity(self):
        entity, predefined = IfcHelper.split_ifc_term("IfcBeam")
        assert entity == "IfcBeam"
        assert predefined is None

    def test_camelcase_only_entity(self):
        entity, predefined = IfcHelper.split_ifc_term("IfcElectricMotor")
        assert entity == "IfcElectricMotor"
        assert predefined is None
