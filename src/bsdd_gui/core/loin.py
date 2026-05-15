from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Type
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_json import BsddClass, BsddClassProperty
    from bsdd_gui.module.iso_export.datamodel import (
        LoinActor,
        LoinInformationDeliveryMilestone,
        LoinPurpose,
        LoinSpecification,
    )


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


def reset(loin: Type["tool.Loin"]):
    """Reset the in-memory LOIN to an empty document. Called by on_new_project."""
    loin.reset()


# ---------------------------------------------------------------------------
# Purposes (Use Cases)
# ---------------------------------------------------------------------------


def add_purpose(
    loin: Type["tool.Loin"], name: str, language: str = "en"
) -> "LoinPurpose":
    return loin.add_purpose(name=name, language=language)


def remove_purpose(loin: Type["tool.Loin"], purpose_guid: UUID) -> None:
    loin.remove_purpose(purpose_guid)


def rename_purpose(
    loin: Type["tool.Loin"], purpose_guid: UUID, name: str, language: str = "en"
) -> None:
    loin.rename_purpose(purpose_guid, name, language)


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------


def add_milestone(
    loin: Type["tool.Loin"],
    name: str,
    language: str = "en",
    date: Optional[datetime] = None,
) -> "LoinInformationDeliveryMilestone":
    return loin.add_milestone(name=name, language=language, date=date)


def remove_milestone(loin: Type["tool.Loin"], milestone_guid: UUID) -> None:
    loin.remove_milestone(milestone_guid)


def rename_milestone(
    loin: Type["tool.Loin"],
    milestone_guid: UUID,
    name: str,
    language: str = "en",
) -> None:
    loin.rename_milestone(milestone_guid, name, language)


def set_milestone_date(
    loin: Type["tool.Loin"], milestone_guid: UUID, date: Optional[datetime]
) -> None:
    loin.set_milestone_date(milestone_guid, date)


# ---------------------------------------------------------------------------
# Actors
# ---------------------------------------------------------------------------


def set_providing_actor(
    loin: Type["tool.Loin"], role: str, **kwargs
) -> "LoinActor":
    return loin.set_providing_actor(role=role, **kwargs)


def set_receiving_actor(
    loin: Type["tool.Loin"], role: str, **kwargs
) -> "LoinActor":
    return loin.set_receiving_actor(role=role, **kwargs)


# ---------------------------------------------------------------------------
# Spec membership
# ---------------------------------------------------------------------------


def is_class_included(
    loin: Type["tool.Loin"],
    bsdd_class: "BsddClass",
    purpose_guid: UUID,
    milestone_guid: UUID,
) -> bool:
    return loin.is_class_included(bsdd_class, purpose_guid, milestone_guid)


def set_class_included(
    loin: Type["tool.Loin"],
    bsdd_class: "BsddClass",
    purpose_guid: UUID,
    milestone_guid: UUID,
    included: bool,
) -> None:
    loin.set_class_included(bsdd_class, purpose_guid, milestone_guid, included)


def is_property_included(
    loin: Type["tool.Loin"],
    bsdd_class: "BsddClass",
    bsdd_property: "BsddClassProperty",
    purpose_guid: UUID,
    milestone_guid: UUID,
) -> bool:
    return loin.is_property_included(
        bsdd_class, bsdd_property, purpose_guid, milestone_guid
    )


def set_property_included(
    loin: Type["tool.Loin"],
    bsdd_class: "BsddClass",
    bsdd_property: "BsddClassProperty",
    purpose_guid: UUID,
    milestone_guid: UUID,
    included: bool,
) -> None:
    """Set a property's membership. Auto-checks the class on True."""
    loin.set_property_included(
        bsdd_class, bsdd_property, purpose_guid, milestone_guid, included
    )


# ---------------------------------------------------------------------------
# XML import / export
# ---------------------------------------------------------------------------


def export_to_xml(loin: Type["tool.Loin"], out_path: str) -> int:
    """Write the current LOIN to *out_path* (ISO 7817-3 XML). Returns spec count."""
    return loin.export_to_xml(out_path)


def import_from_xml(loin: Type["tool.Loin"], in_path: str) -> None:
    """Replace the current LOIN with the contents of *in_path*."""
    loin.import_from_xml(in_path)
