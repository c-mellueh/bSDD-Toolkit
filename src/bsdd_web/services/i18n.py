"""Tiny translation table for strings that end up in exported files."""

from __future__ import annotations

_DE = {
    "Name": "Name",
    "Parent Code": "Elternklasse",
    "Identifier": "Identifikator",
    "Definition": "Definition",
    "Property": "Merkmal",
    "PropertySet": "Merkmalsgruppe",
    "Datatype": "Datentyp",
    "Values": "Werte",
    "Overview": "Übersicht",
}


def t(text: str, lang: str = "en") -> str:
    if lang.lower().startswith("de"):
        return _DE.get(text, text)
    return text
