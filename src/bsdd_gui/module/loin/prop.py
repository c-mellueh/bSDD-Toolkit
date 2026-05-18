from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties,WidgetProperties,ViewProperties
from typing import TYPE_CHECKING, Dict, Optional, Set, Tuple
from uuid import UUID

if TYPE_CHECKING:
    from bsdd_gui.module.iso_export.datamodel import (
        LoinActor,
        LoinInformationDeliveryMilestone,
        LoinLevelOfInformationNeed,
        LoinPurpose,
        LoinSpecification,
    )

ClassCode = str
PropertyCode = str
# (pset_name, property_code) — None means "the property set as a whole" (not used yet)
PropertyKey = Tuple[str, PropertyCode]
SpecKey = Tuple[UUID, UUID]


# ---------------------------------------------------------------------------
# Membership cache
# ---------------------------------------------------------------------------
# The LOIN data model stores specs as a flat list of LoinSpecification objects.
# At UI time we need fast lookups of "is class X in spec (purpose_guid,
# milestone_guid)?" and "is property Y in that spec?". A pair of dicts keyed
# by (purpose_guid, milestone_guid) gives us that.


class LoinProperties(ActionsProperties,WidgetProperties):
    def __init__(self):
        super().__init__()
        # The in-memory LOIN document. Created fresh per project.
        self.loin: Optional["LoinLevelOfInformationNeed"] = None

        # Ordered list of purposes / milestones (mirrors LOIN content but keeps
        # GUI-friendly ordering distinct from the XML order in the model).
        self.purposes: list["LoinPurpose"] = []
        self.milestones: list["LoinInformationDeliveryMilestone"] = []

        # Global actor pair shared by every generated LoinSpecification.
        self.providing_actor: Optional["LoinActor"] = None
        self.receiving_actor: Optional["LoinActor"] = None

        # Spec membership caches:
        #   (purpose_guid, milestone_guid) -> set of class codes / property keys
        self.classes_in_spec: Dict[SpecKey, Set[ClassCode]] = {}
        self.properties_in_spec: Dict[
            SpecKey, Dict[ClassCode, Set[PropertyKey]]
        ] = {}

        # Underlying LoinSpecification objects, keyed the same way as above.
        # Lazily created when the user first checks something.
        self.specs: Dict[SpecKey, "LoinSpecification"] = {}

        # The signal hub (QObject so we can emit Qt signals).
        self.added_classes:set[ClassCode] = set()


class PPClassViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()


class PPPropertyViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
