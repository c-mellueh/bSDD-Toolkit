"""
Tests for the PropertyTableWidget module (tool/property_table_widget.py).

Covers get_properties_from_mime_payload which is pure Python.
"""

from __future__ import annotations

from bsdd_json.models import BsddDictionary, BsddProperty

from bsdd_gui.tool import PropertyTableWidget


def _make_dict(*properties: BsddProperty) -> BsddDictionary:
    d = BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="D",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
    )
    d.Properties.extend(properties)
    return d


def _prop_json(code: str, name: str = None, data_type: str = "String") -> dict:
    return {"Code": code, "Name": name or code, "DataType": data_type}


# ---------------------------------------------------------------------------
# get_properties_from_mime_payload
# ---------------------------------------------------------------------------


class TestGetPropertiesFromMimePayload:
    def test_returns_new_properties(self):
        d = _make_dict()
        payload = {"properties": [_prop_json("P1")]}
        result = PropertyTableWidget.get_properties_from_mime_payload(payload, d)
        assert len(result) == 1
        assert result[0].Code == "P1"

    def test_skips_properties_already_in_dictionary(self):
        existing = BsddProperty(Code="P1", Name="P1", DataType="String")
        d = _make_dict(existing)
        payload = {"properties": [_prop_json("P1"), _prop_json("P2")]}
        result = PropertyTableWidget.get_properties_from_mime_payload(payload, d)
        codes = [p.Code for p in result]
        assert "P1" not in codes
        assert "P2" in codes

    def test_returns_false_when_properties_is_not_a_list(self):
        d = _make_dict()
        payload = {"properties": "not_a_list"}
        assert PropertyTableWidget.get_properties_from_mime_payload(payload, d) is False

    def test_returns_empty_list_when_all_already_exist(self):
        existing = BsddProperty(Code="P1", Name="P1", DataType="String")
        d = _make_dict(existing)
        payload = {"properties": [_prop_json("P1")]}
        result = PropertyTableWidget.get_properties_from_mime_payload(payload, d)
        assert result == []

    def test_skips_invalid_property_dicts(self):
        d = _make_dict()
        # "DataType" is required by BsddProperty — omitting it should cause model_validate to fail
        payload = {"properties": [{"Code": "BAD"}, _prop_json("GOOD")]}
        result = PropertyTableWidget.get_properties_from_mime_payload(payload, d)
        codes = [p.Code for p in result]
        assert "GOOD" in codes

    def test_empty_properties_list_returns_empty(self):
        d = _make_dict()
        payload = {"properties": []}
        result = PropertyTableWidget.get_properties_from_mime_payload(payload, d)
        assert result == []

    def test_missing_properties_key_returns_empty(self):
        d = _make_dict()
        payload = {}
        result = PropertyTableWidget.get_properties_from_mime_payload(payload, d)
        assert result == []
