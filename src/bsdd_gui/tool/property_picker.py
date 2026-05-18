from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict
import logging
from PySide6.QtCore import Signal
from uuid import UUID, uuid4

from datetime import datetime
import bsdd_gui
from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import class_utils
from bsdd_gui.presets.tool_presets import (
    ActionTool,
    WidgetTool,
    WidgetSignals,
    ItemViewTool,
    ViewSignals,
)
from bsdd_gui.module.property_picker import ui, trigger, model_views, models, constants
from bsdd_gui.module.iso_export.datamodel import (
    DtMultiLangText,
    DtRef,
    IsoGroupOfProperties,
    IsoObjectType,
    LoinActor,
    LoinAlphanumericalInformation,
    LoinGroupsOfProperties,
    LoinInformationDeliveryMilestone,
    LoinLevelOfInformationNeed,
    LoinPrerequisites,
    LoinPurpose,
    LoinSpecification,
    LoinSpecificationPerObjectType,
)

if TYPE_CHECKING:
    from bsdd_gui.module.property_picker.prop import (
        PropertyPickerProperties,
        PPClassViewProperties,
        PPPropertyViewProperties,
        ClassCode,
        PropertyCode,
    )




def _now() -> datetime:
    return datetime.now()


class PsetDict(TypedDict):
    checked: bool
    properties: dict[str, bool]


class Signals(WidgetSignals):
    purposes_changed = Signal()
    milestones_changed = Signal()
    actors_changed = Signal()
    spec_membership_changed = Signal()
    # Emitted when added_classes grows/shrinks (rows change in ClassModel).
    added_classes_changed = Signal()
    # Coarse signal: anything about the LOIN tree changed (used to reset views)
    loin_reset = Signal()


class PropertyPicker(ActionTool, WidgetTool):
    signals = Signals()



    @classmethod
    def get_properties(cls) -> PropertyPickerProperties:
        return bsdd_gui.PropertyPickerProperties

    @classmethod
    def get_signals(cls) -> Signals:
        return super().get_signals()

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
        super().connect_widget_signals(widget)

    @classmethod
    def get_loin(cls) -> Optional[LoinLevelOfInformationNeed]:
        """Return the LOIN root, or None if no specifications exist yet.

        The XSD requires LoinLevelOfInformationNeed.specifications to have at
        least one entry, so an empty draft is represented by None on disk and
        in memory.
        """
        props = cls.get_properties()
        specs = list(props.specs.values())
        if not specs:
            return None
        return LoinLevelOfInformationNeed(specifications=specs)

    @classmethod
    def has_specs(cls) -> bool:
        return bool(cls.get_properties().specs)

    @classmethod
    def get_checked_classes(
        cls,
        active_specifications: list[LoinSpecification],bsdd_dictionary: BsddDictionary
    ) -> list[BsddClass]:
        """Return BsddClass objects included in at least one of the given specs."""
        props = cls.get_properties()

        if bsdd_dictionary is None:
            return []
        existing = {c.Code: c for c in bsdd_dictionary.Classes}
        checked_codes: set[str] = set()
        for spec in active_specifications:
            key = cls._get_spec_key(spec)
            checked_codes.update(props.classes_in_spec.get(key, set()))
        return [existing[code] for code in checked_codes if code in existing]

    @classmethod
    def _get_spec_key(cls,spec: LoinSpecification) -> tuple[UUID, UUID]:
        return spec.prerequisites.purpose.guid, spec.prerequisites.information_delivery_milestone.guid

    @classmethod
    def get_checked_properties(
        cls,
        active_specifications: list[LoinSpecification],
        bsdd_dictionary: BsddDictionary,
    ) -> dict[str, dict[str, PsetDict]]:
        """Return property check state for every class/pset/property.

        A pset or property entry is ``True`` when it is included in at least
        one of *active_specifications*.
        """

        if bsdd_dictionary is None:
            return {}

        result: dict[str, dict[str, PsetDict]] = {}

        for bsdd_class in bsdd_dictionary.Classes:
            if not cls.is_class_added(bsdd_class):
                continue
            psets: dict[str, PsetDict] = {}
            for cp in bsdd_class.ClassProperties:
                pset_name = cp.PropertySet or ""
                prop_checked = False
                for spec in active_specifications:
                    p_guid, m_guid = cls._get_spec_key(spec)
                    if cls.is_property_included(bsdd_class, cp, p_guid, m_guid):
                        prop_checked = True
    
                entry = psets.setdefault(pset_name, {"checked": False, "properties": {}})
                entry["properties"][cp.Code] = prop_checked
                if prop_checked:
                    entry["checked"] = True

            if psets:
                result[bsdd_class.Code] = psets

        return result

    @classmethod
    def get_checked_predefined_properties(
        cls,
        active_specifications: list[LoinSpecification],
        bsdd_dictionary: BsddDictionary,
    ) -> dict[str, set[str]]:
        """Return pset_name → set of property codes checked in at least one spec.

        Aggregates across all added classes exactly like the pset tree view:
        each unique (pset, property_code) pair appears once and is included
        when ANY class that owns it has it checked in any active specification.
        """
        if bsdd_dictionary is None:
            return {}

        # (pset_name, prop_code) → True once confirmed checked
        seen: dict[tuple[str, str], bool] = {}

        for bsdd_class in bsdd_dictionary.Classes:
            if not cls.is_class_added(bsdd_class):
                continue
            for cp in bsdd_class.ClassProperties:
                key = (cp.PropertySet or "", cp.Code or "")
                if seen.get(key):
                    continue  # already confirmed checked — skip further lookups
                for spec in active_specifications:
                    p_guid, m_guid = cls._get_spec_key(spec)
                    if cls.is_property_included(bsdd_class, cp, p_guid, m_guid):
                        seen[key] = True
                        break
                else:
                    seen.setdefault(key, False)

        result: dict[str, set[str]] = {}
        for (pset, code), checked in seen.items():
            if checked:
                result.setdefault(pset, set()).add(code)
        return result

    @classmethod
    def reset(cls) -> None:
        """Wipe the LOIN back to a fresh document.

        A freshly-reset LOIN is not actually empty — it carries one base
        Purpose and one base Milestone so the UC × MS grid is immediately
        usable. The user can rename or remove either of them via the
        FilterTableWindow.
        """
        props = cls.get_properties()
        props.loin = None
        props.purposes = []
        props.milestones = []
        props.providing_actor = None
        props.receiving_actor = None
        props.classes_in_spec = {}
        props.added_classes = set()
        props.properties_in_spec = {}
        props.specs = {}

        # Seed the base UC/MS pair (signals are emitted in bulk below).
        default_purpose = LoinPurpose(
            guid=uuid4(),
            names=[DtMultiLangText(language="en", text=constants.DEFAULT_PURPOSE_NAME)],
        )
        default_milestone = LoinInformationDeliveryMilestone(
            guid=uuid4(),
            names=[DtMultiLangText(language="en", text=constants.DEFAULT_MILESTONE_NAME)],
        )
        props.purposes.append(default_purpose)
        props.milestones.append(default_milestone)
        cls.get_or_create_spec(default_purpose.guid, default_milestone.guid)

        cls.get_signals().loin_reset.emit()
        cls.get_signals().purposes_changed.emit()
        cls.get_signals().milestones_changed.emit()
        cls.get_signals().actors_changed.emit()
        cls.get_signals().spec_membership_changed.emit()

    @classmethod
    def get_purposes(cls) -> list[LoinPurpose]:
        return list(cls.get_properties().purposes)

    @classmethod
    def add_purpose(cls, name: str, language: str = "en") -> LoinPurpose:
        purpose = LoinPurpose(
            guid=uuid4(),
            names=[DtMultiLangText(language=language, text=name)],
        )
        cls.get_properties().purposes.append(purpose)
        for milestone in cls.get_properties().milestones:
            cls.get_or_create_spec(purpose.guid, milestone.guid)
        cls.get_signals().purposes_changed.emit()
        return purpose

    @classmethod
    def remove_purpose(cls, purpose_guid: UUID) -> None:
        props = cls.get_properties()
        props.purposes = [p for p in props.purposes if p.guid != purpose_guid]
        # Drop dependent specs.
        for key in list(props.specs.keys()):
            if key[0] == purpose_guid:
                props.specs.pop(key, None)
                props.classes_in_spec.pop(key, None)
                props.properties_in_spec.pop(key, None)
        cls.get_signals().purposes_changed.emit()
        cls.get_signals().spec_membership_changed.emit()

    @classmethod
    def rename_purpose(cls, purpose_guid: UUID, name: str, language: str = "en") -> None:
        for p in cls.get_properties().purposes:
            if p.guid == purpose_guid:
                p.names = [DtMultiLangText(language=language, text=name)]
                cls.get_signals().purposes_changed.emit()
                return

    @classmethod
    def purpose_display_name(cls, purpose: LoinPurpose) -> str:
        if purpose.names:
            return purpose.names[0].text
        return str(purpose.guid)

    # ------------------------------------------------------------------ milestones

    @classmethod
    def get_milestones(cls) -> list[LoinInformationDeliveryMilestone]:
        return list(cls.get_properties().milestones)

    @classmethod
    def add_milestone(
        cls,
        name: str,
        language: str = "en",
        date: Optional[datetime] = None,
    ) -> LoinInformationDeliveryMilestone:
        milestone = LoinInformationDeliveryMilestone(
            guid=uuid4(),
            date=date,
            names=[DtMultiLangText(language=language, text=name)],
        )
        cls.get_properties().milestones.append(milestone)
        for purpose in cls.get_properties().purposes:
            cls.get_or_create_spec(purpose.guid, milestone.guid)
        cls.get_signals().milestones_changed.emit()
        return milestone

    @classmethod
    def remove_milestone(cls, milestone_guid: UUID) -> None:
        props = cls.get_properties()
        props.milestones = [m for m in props.milestones if m.guid != milestone_guid]
        for key in list(props.specs.keys()):
            if key[1] == milestone_guid:
                props.specs.pop(key, None)
                props.classes_in_spec.pop(key, None)
                props.properties_in_spec.pop(key, None)
        cls.get_signals().milestones_changed.emit()
        cls.get_signals().spec_membership_changed.emit()

    @classmethod
    def rename_milestone(
        cls,
        milestone_guid: UUID,
        name: str,
        language: str = "en",
    ) -> None:
        for m in cls.get_properties().milestones:
            if m.guid == milestone_guid:
                m.names = [DtMultiLangText(language=language, text=name)]
                cls.get_signals().milestones_changed.emit()
                return

    @classmethod
    def set_milestone_date(cls, milestone_guid: UUID, date: Optional[datetime]) -> None:
        for m in cls.get_properties().milestones:
            if m.guid == milestone_guid:
                m.date = date
                cls.get_signals().milestones_changed.emit()
                return

    @classmethod
    def milestone_display_name(cls, milestone: LoinInformationDeliveryMilestone) -> str:
        if milestone.names:
            return milestone.names[0].text
        return str(milestone.guid)

    # ------------------------------------------------------------------ actors

    @classmethod
    def get_providing_actor(cls) -> Optional[LoinActor]:
        return cls.get_properties().providing_actor

    @classmethod
    def get_receiving_actor(cls) -> Optional[LoinActor]:
        return cls.get_properties().receiving_actor

    @classmethod
    def set_providing_actor(
        cls,
        role: str,
        language: str = "en",
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        affiliation: Optional[str] = None,
        email_address: Optional[str] = None,
    ) -> LoinActor:
        actor = LoinActor(
            guid=uuid4(),
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            affiliation=affiliation,
            role=DtMultiLangText(language=language, text=role),
            email_address=email_address,
        )
        cls.get_properties().providing_actor = actor
        cls._refresh_spec_prerequisites()
        cls.get_signals().actors_changed.emit()
        return actor

    @classmethod
    def set_receiving_actor(
        cls,
        role: str,
        language: str = "en",
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        affiliation: Optional[str] = None,
        email_address: Optional[str] = None,
    ) -> LoinActor:
        actor = LoinActor(
            guid=uuid4(),
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            affiliation=affiliation,
            role=DtMultiLangText(language=language, text=role),
            email_address=email_address,
        )
        cls.get_properties().receiving_actor = actor
        cls._refresh_spec_prerequisites()
        cls.get_signals().actors_changed.emit()
        return actor

    @classmethod
    def _refresh_spec_prerequisites(cls) -> None:
        """Update the actor pair on every existing spec to match the globals."""
        for spec in cls.get_properties().specs.values():
            prereq = spec.prerequisites
            if cls.get_providing_actor() is not None:
                prereq.providing_actor = cls.get_providing_actor()
            if cls.get_receiving_actor() is not None:
                prereq.receiving_actor = cls.get_receiving_actor()

    # ------------------------------------------------------------------ spec creation

    @classmethod
    def get_or_create_spec(cls, purpose_guid: UUID, milestone_guid: UUID) -> LoinSpecification:
        """Return the LoinSpecification for this (purpose, milestone). Creates it on demand."""
        props = cls.get_properties()
        key = (purpose_guid, milestone_guid)
        existing = props.specs.get(key)
        if existing is not None:
            return existing

        purpose = next((p for p in props.purposes if p.guid == purpose_guid), None)
        milestone = next((m for m in props.milestones if m.guid == milestone_guid), None)
        if purpose is None or milestone is None:
            raise KeyError(
                f"Cannot create spec: missing purpose {purpose_guid} "
                f"or milestone {milestone_guid}"
            )

        providing = props.providing_actor or LoinActor(
            guid=uuid4(),
            role=DtMultiLangText(language="en", text="Provider"),
        )
        receiving = props.receiving_actor or LoinActor(
            guid=uuid4(),
            role=DtMultiLangText(language="en", text="Receiver"),
        )

        spec_name = (
            f"{cls.purpose_display_name(purpose)} – " f"{cls.milestone_display_name(milestone)}"
        )
        spec = LoinSpecification(
            name=spec_name,
            guid=uuid4(),
            prerequisites=LoinPrerequisites(
                guid=uuid4(),
                purpose=purpose,
                information_delivery_milestone=milestone,
                providing_actor=providing,
                receiving_actor=receiving,
            ),
            specifications_per_object_type=[],
        )
        props.specs[key] = spec
        props.classes_in_spec.setdefault(key, set())
        props.properties_in_spec.setdefault(key, {})
        return spec

    # ------------------------------------------------------------------ membership

    @classmethod
    def is_class_included(
        cls,
        bsdd_class: "BsddClass",
        purpose_guid: UUID,
        milestone_guid: UUID,
    ) -> bool:
        return bsdd_class.Code in cls.get_properties().classes_in_spec.get(
            (purpose_guid, milestone_guid), set()
        )

    @classmethod
    def is_class_added(cls, bsdd_class: BsddClass) -> bool:
        return bsdd_class.Code in cls.get_properties().added_classes

    @classmethod
    def apply_checkstate_to_children(
        cls,
        bsdd_class: BsddClass,
        purpose_guid: UUID,
        milestone_guid: UUID,
    ) -> None:
        """Propagate bsdd_class's check state for a UC×MS to all its descendants."""
        included = cls.is_class_included(bsdd_class, purpose_guid, milestone_guid)
        props = cls.get_properties()

        def walk(parent: BsddClass) -> None:
            for child in class_utils.get_children(parent):
                if child.Code not in props.added_classes:
                    continue
                cls._set_class_included_silent(child, purpose_guid, milestone_guid, included)
                walk(child)

        walk(bsdd_class)
        cls.get_signals().spec_membership_changed.emit()
        cls.get_signals().added_classes_changed.emit()

    @classmethod
    def remove_class(cls, bsdd_class: BsddClass) -> None:
        """Remove a class and all its descendants from the property picker."""
        props = cls.get_properties()

        # Collect the class plus every descendant that is currently added.
        to_remove: list[BsddClass] = []

        def _collect(parent: BsddClass) -> None:
            to_remove.append(parent)
            for child in class_utils.get_children(parent):
                if child.Code in props.added_classes:
                    _collect(child)

        _collect(bsdd_class)

        for bc in to_remove:
            code = bc.Code
            props.added_classes.discard(code)
            for key in list(props.specs.keys()):
                props.classes_in_spec.get(key, set()).discard(code)
                props.properties_in_spec.get(key, {}).pop(code, None)
                spec = props.specs.get(key)
                if spec is not None:
                    cls._remove_class_from_spec(spec, bc)

        cls.get_signals().added_classes_changed.emit()

    @classmethod
    def add_classes(cls, codes: list[str], bsdd_dictionary: BsddDictionary) -> None:
        """Add classes and their ancestors to added_classes, then refresh the view."""
        props = cls.get_properties()
        existing = {c.Code: c for c in bsdd_dictionary.Classes}
        to_add: set[str] = set()
        for code in codes:
            if code not in existing:
                continue
            to_add.add(code)
            parent = existing.get(existing[code].ParentClassCode)
            while parent:
                if parent.Code in to_add or parent.Code in props.added_classes:
                    break
                to_add.add(parent.Code)
                parent = existing.get(parent.ParentClassCode)
        if not to_add:
            return
        props.added_classes.update(to_add)
        cls.get_signals().added_classes_changed.emit()

    @classmethod
    def set_class_included(
        cls,
        bsdd_class: "BsddClass",
        purpose_guid: UUID,
        milestone_guid: UUID,
        included: bool,
    ) -> None:
        cls._set_class_included_silent(bsdd_class, purpose_guid, milestone_guid, included)
        cls.get_signals().spec_membership_changed.emit()

    @classmethod
    def is_property_included(
        cls,
        bsdd_class: "BsddClass",
        bsdd_property: "BsddClassProperty",
        purpose_guid: UUID,
        milestone_guid: UUID,
    ) -> bool:
        props = cls.get_properties()
        per_class = props.properties_in_spec.get((purpose_guid, milestone_guid), {})
        return (bsdd_property.PropertySet, bsdd_property.Code) in per_class.get(
            bsdd_class.Code, set()
        )

    @classmethod
    def set_property_included(
        cls,
        bsdd_class: "BsddClass",
        bsdd_property: "BsddClassProperty",
        purpose_guid: UUID,
        milestone_guid: UUID,
        included: bool,
    ) -> None:
        cls._set_property_included_silent(bsdd_class, bsdd_property, purpose_guid, milestone_guid, included)
        cls.get_signals().spec_membership_changed.emit()

    @classmethod
    def _set_class_included_silent(
        cls,
        bsdd_class: "BsddClass",
        purpose_guid: UUID,
        milestone_guid: UUID,
        included: bool,
    ) -> None:
        """Like set_class_included but without emitting spec_membership_changed."""
        props = cls.get_properties()
        key = (purpose_guid, milestone_guid)
        bucket = props.classes_in_spec.setdefault(key, set())
        if included:
            if bsdd_class.Code in bucket:
                return
            if bsdd_class.Code not in props.added_classes:
                props.added_classes.add(bsdd_class.Code)
            bucket.add(bsdd_class.Code)
            spec = cls.get_or_create_spec(purpose_guid, milestone_guid)
            cls._add_class_to_spec(spec, bsdd_class)
        else:
            if bsdd_class.Code not in bucket:
                return
            bucket.discard(bsdd_class.Code)
            props.properties_in_spec.get(key, {}).pop(bsdd_class.Code, None)
            spec = props.specs.get(key)
            if spec is not None:
                cls._remove_class_from_spec(spec, bsdd_class)

    @classmethod
    def _set_property_included_silent(
        cls,
        bsdd_class: "BsddClass",
        bsdd_property: "BsddClassProperty",
        purpose_guid: UUID,
        milestone_guid: UUID,
        included: bool,
    ) -> None:
        """Like set_property_included but without emitting spec_membership_changed."""
        props = cls.get_properties()
        key = (purpose_guid, milestone_guid)
        per_class = props.properties_in_spec.setdefault(key, {})
        bucket = per_class.setdefault(bsdd_class.Code, set())
        prop_key = (bsdd_property.PropertySet, bsdd_property.Code)
        if included:
            cls._set_class_included_silent(bsdd_class, purpose_guid, milestone_guid, True)
            if prop_key in bucket:
                return
            bucket.add(prop_key)
            spec = cls.get_or_create_spec(purpose_guid, milestone_guid)
            spec_per_obj = cls._find_spec_per_object_type(spec, bsdd_class)
            if spec_per_obj is not None:
                cls._add_property_to_spec_per_obj(spec_per_obj, bsdd_property)
        else:
            if prop_key not in bucket:
                return
            bucket.discard(prop_key)
            spec = props.specs.get(key)
            if spec is not None:
                spec_per_obj = cls._find_spec_per_object_type(spec, bsdd_class)
                if spec_per_obj is not None:
                    cls._remove_property_from_spec_per_obj(spec_per_obj, bsdd_property)

    @classmethod
    def set_pset_included(
        cls,
        pset_classes: "list[tuple[BsddClass, list[BsddClassProperty]]]",
        purpose_guid: UUID,
        milestone_guid: UUID,
        included: bool,
    ) -> None:
        """Set all properties of a pset across multiple classes, emitting the signal once."""
        for bsdd_class, props in pset_classes:
            for cp in props:
                cls._set_property_included_silent(bsdd_class, cp, purpose_guid, milestone_guid, included)
        cls.get_signals().spec_membership_changed.emit()

    # ----------------------------------------- LoinSpecificationPerObjectType helpers

    @classmethod
    def _add_class_to_spec(cls, spec: LoinSpecification, bsdd_class: "BsddClass") -> None:
        if cls._find_spec_per_object_type(spec, bsdd_class) is not None:
            return
        object_type = IsoObjectType(
            guid=uuid4(),
            date_of_creation=_now(),
            names=[DtMultiLangText(language="en", text=bsdd_class.Name or bsdd_class.Code)],
        )
        spec_per_obj = LoinSpecificationPerObjectType(
            guid=uuid4(),
            date_of_creation=_now(),
            names=[DtMultiLangText(language="en", text=bsdd_class.Name or bsdd_class.Code)],
            object_type=object_type,
            alphanumerical_information=LoinAlphanumericalInformation(
                guid=uuid4(),
                groups_of_properties=LoinGroupsOfProperties(
                    group_of_properties=[],
                    group_of_properties_refs=[],
                ),
            ),
        )
        # Remember which bSDD class this represents — stored as an attribute
        # on the Pydantic instance, not part of the XML schema.
        spec_per_obj.__dict__["_bsdd_class_code"] = bsdd_class.Code
        spec.specifications_per_object_type.append(spec_per_obj)

    @classmethod
    def _remove_class_from_spec(cls, spec: LoinSpecification, bsdd_class: "BsddClass") -> None:
        spec.specifications_per_object_type = [
            s
            for s in spec.specifications_per_object_type
            if s.__dict__.get("_bsdd_class_code") != bsdd_class.Code
        ]

    @classmethod
    def _find_spec_per_object_type(
        cls, spec: LoinSpecification, bsdd_class: "BsddClass"
    ) -> Optional[LoinSpecificationPerObjectType]:
        for s in spec.specifications_per_object_type:
            if s.__dict__.get("_bsdd_class_code") == bsdd_class.Code:
                return s
        return None

    @classmethod
    def _add_property_to_spec_per_obj(
        cls,
        spec_per_obj: LoinSpecificationPerObjectType,
        bsdd_property: "BsddClassProperty",
    ) -> None:
        alpha = spec_per_obj.alphanumerical_information
        if alpha is None:
            alpha = LoinAlphanumericalInformation(
                guid=uuid4(),
                groups_of_properties=LoinGroupsOfProperties(),
            )
            spec_per_obj.alphanumerical_information = alpha
        if alpha.groups_of_properties is None:
            alpha.groups_of_properties = LoinGroupsOfProperties()

        # Build the property ref first so we can create the group with it
        # (IsoGroupOfProperties.has_property_refs has min_length=1).
        ref = cls._property_ref(bsdd_property)

        pset = bsdd_property.PropertySet
        group = cls._find_group_for_pset(alpha.groups_of_properties, pset)
        if group is None:
            group = IsoGroupOfProperties(
                guid=uuid4(),
                date_of_creation=_now(),
                names=[DtMultiLangText(language="en", text=pset)],
                has_property_refs=[ref],
            )
            group.__dict__["_pset"] = pset
            alpha.groups_of_properties.group_of_properties.append(group)
            return

        # de-dup
        if any(
            (
                (r.reference_uri == ref.reference_uri and ref.reference_uri is not None)
                or (r.guid == ref.guid and ref.guid is not None)
            )
            for r in group.has_property_refs
        ):
            return
        group.has_property_refs.append(ref)

    @classmethod
    def _remove_property_from_spec_per_obj(
        cls,
        spec_per_obj: LoinSpecificationPerObjectType,
        bsdd_property: "BsddClassProperty",
    ) -> None:
        alpha = spec_per_obj.alphanumerical_information
        if alpha is None or alpha.groups_of_properties is None:
            return
        pset = bsdd_property.PropertySet
        group = cls._find_group_for_pset(alpha.groups_of_properties, pset)
        if group is None:
            return
        target = cls._property_ref(bsdd_property)
        group.has_property_refs = [
            r
            for r in group.has_property_refs
            if not (
                (r.reference_uri == target.reference_uri and target.reference_uri is not None)
                or (r.guid == target.guid and target.guid is not None)
            )
        ]
        if not group.has_property_refs:
            alpha.groups_of_properties.group_of_properties = [
                g for g in alpha.groups_of_properties.group_of_properties if g is not group
            ]

    @classmethod
    def _find_group_for_pset(
        cls,
        groups: LoinGroupsOfProperties,
        pset: str,
    ) -> Optional[IsoGroupOfProperties]:
        for g in groups.group_of_properties:
            if g.__dict__.get("_pset") == pset:
                return g
        return None

    @classmethod
    def _property_ref(cls, bsdd_property: "BsddClassProperty") -> DtRef:
        """Build a DtRef for a bSDD property.

        Prefers an explicit PropertyUri. For internally-referenced properties
        (PropertyCode only) builds the canonical bSDD URI via build_bsdd_uri.
        """
        uri = bsdd_property.PropertyUri or bsdd_property.OwnedUri

        if not uri:
            inner = prop_utils.get_internal_property(bsdd_property)
            dictionary = prop_utils.get_dictionary_from_property(bsdd_property)
            if inner is not None and dictionary is not None:
                uri = prop_utils.build_bsdd_uri(inner, dictionary)

        return DtRef(reference_uri=uri)

    # ------------------------------------------------------------------ XML I/O

    @classmethod
    def export_to_xml(cls, out_path: str) -> int:
        loin = cls.get_loin()
        if loin is None:
            raise ValueError(
                "Cannot export an empty LOIN — add at least one Purpose, "
                "Milestone and class selection first."
            )
        xml_bytes = loin.to_xml(
            encoding="UTF-8",
            xml_declaration=True,
            exclude_none=False,
            exclude_unset=True,
        )
        with open(out_path, "wb") as f:
            f.write(xml_bytes)
        return len(loin.specifications)

    @classmethod
    def request_xml_import(cls, widget: ui.Widget) :
        trigger.import_xml(widget)

    @classmethod
    def request_xml_export(cls, widget: ui.Widget) :
        trigger.export_xml(widget)

    @classmethod
    def _resolve_property_uri_to_code(
        cls,
        bsdd_class: "BsddClass",
        pset: str,
        uri: str,
        bsdd_dictionary: "BsddDictionary",
    ) -> Optional[str]:
        """Return the BsddClassProperty.Code whose URI matches *uri*.

        Uses get_property_by_uri so version segments in the URI are ignored.
        """
        bsdd_prop = prop_utils.get_property_by_uri(uri, bsdd_dictionary)
        if bsdd_prop is None:
            return None
        for cp in bsdd_class.ClassProperties:
            if cp.PropertySet != pset:
                continue
            if cp.PropertyCode == bsdd_prop.Code:
                return cp.Code
            if cp.PropertyUri and cp.PropertyUri == uri:
                return cp.Code
        return None

    @classmethod
    def _adopt_loin(cls, loin: LoinLevelOfInformationNeed, bsdd_dictionary: BsddDictionary) -> None:
        """Replace state from a freshly parsed LoinLevelOfInformationNeed.

        Membership caches and the global actor pair are rebuilt from the spec
        list. The first spec's actors are used as the global pair.
        """
        props = cls.get_properties()
        props.loin = loin
        props.purposes = []
        props.milestones = []
        props.providing_actor = None
        props.receiving_actor = None
        props.classes_in_spec = {}
        props.added_classes = set()
        props.properties_in_spec = {}
        props.specs = {}

        seen_purposes: dict[UUID, LoinPurpose] = {}
        seen_milestones: dict[UUID, LoinInformationDeliveryMilestone] = {}
        existing_classes = {c.Code: c for c in bsdd_dictionary.Classes}

        for spec in loin.specifications:
            purpose = spec.prerequisites.purpose
            milestone = spec.prerequisites.information_delivery_milestone
            seen_purposes.setdefault(purpose.guid, purpose)
            seen_milestones.setdefault(milestone.guid, milestone)
            if props.providing_actor is None:
                props.providing_actor = spec.prerequisites.providing_actor
            if props.receiving_actor is None:
                props.receiving_actor = spec.prerequisites.receiving_actor

            key = cls._get_spec_key(spec)
            props.specs[key] = spec
            class_codes: set[str] = set()
            prop_buckets: dict[str, set[tuple[str, str]]] = {}
            for s in spec.specifications_per_object_type:
                code = s.__dict__.get("_bsdd_class_code")
                if code is None and s.object_type.names:
                    code = s.object_type.names[0].text
                if not code:
                    continue
                class_codes.add(code)
                s.__dict__["_bsdd_class_code"] = code
                # Rehydrate property membership from any groups present.
                if (
                    s.alphanumerical_information
                    and s.alphanumerical_information.groups_of_properties
                ):
                    for g in s.alphanumerical_information.groups_of_properties.group_of_properties:
                        pset = g.__dict__.get("_pset")
                        if pset is None and g.names:
                            pset = g.names[0].text
                            g.__dict__["_pset"] = pset
                        if not pset:
                            continue
                        bsdd_class = existing_classes.get(code)
                        for ref in g.has_property_refs:
                            uri = ref.reference_uri or (str(ref.guid) if ref.guid else None)
                            if uri is None:
                                continue
                            prop_code = cls._resolve_property_uri_to_code(
                                bsdd_class, pset, uri, bsdd_dictionary
                            ) if bsdd_class else None
                            if prop_code:
                                prop_buckets.setdefault(code, set()).add((pset, prop_code))

            added_classes = set(class_codes)
            # also add the Parent classes so they also get shown
            for c in list(added_classes):
                bsdd_class = existing_classes.get(c)
                if not bsdd_class:
                    continue

                parent = existing_classes.get(bsdd_class.ParentClassCode)
                while parent:
                    if parent.Code in added_classes:
                        parent = None
                    else:
                        added_classes.add(parent.Code)
                        parent = existing_classes.get(parent.ParentClassCode)

            cls.get_properties().added_classes.update(added_classes)
            props.classes_in_spec[key] = class_codes
            props.properties_in_spec[key] = prop_buckets

        props.purposes = list(seen_purposes.values())
        props.milestones = list(seen_milestones.values())

        cls.get_signals().loin_reset.emit()
        cls.get_signals().purposes_changed.emit()
        cls.get_signals().milestones_changed.emit()
        cls.get_signals().actors_changed.emit()
        cls.get_signals().spec_membership_changed.emit()


class ClassSignals(ViewSignals):
    set_inheritance_requested = Signal(bool, model_views.ClassView)


class PPClassView(ItemViewTool):
    signals = ClassSignals()

    @classmethod
    def get_properties(cls) -> PPClassViewProperties:
        return bsdd_gui.PPClassViewProperties  #

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
    def request_set_inheritance(cls, state: bool, view: model_views.ClassView):
        cls.signals.set_inheritance_requested.emit(state, view)

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.set_inheritance_requested.connect(cls.set_checkstate_inheritance)
        return super().connect_internal_signals()


    @classmethod
    def build_full_check_dict(cls, view: model_views.ClassView, bsdd_dictionary: BsddDictionary):
        partial = cls.get_checked_classes(view)
        full = {}

        def walk(node: BsddClass, inherited: bool):
            state = partial.get(node.Code, inherited)
            full[node.Code] = state
            for child in class_utils.get_children(node, bsdd_dictionary):
                walk(child, state)

        for root in class_utils.get_root_classes(bsdd_dictionary):
            walk(root, True)

        return full


    @classmethod
    def set_checkstate_inheritance(cls, state: bool, view: model_views.ClassView):
        class_model: models.ClassTreeModel = view.model().sourceModel()
        class_model.set_checkstate_inheritance(state)

    @classmethod
    def get_property_view(cls, class_view: model_views.ClassView) -> model_views.PropertyView:
        widget: ui.Widget = class_view.parent().parent().parent().parent()
        return widget.tv_properties

    @classmethod
    def on_current_changed(cls, view, curr, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = curr
        cls.signals.selection_changed.emit(view, index.internalPointer())


class PropertySignals(ViewSignals):
    pass


class PPPropertyView(ItemViewTool):
    signals = PropertySignals()

    @classmethod
    def get_properties(cls) -> PPPropertyViewProperties:
        return bsdd_gui.PPPropertyViewProperties

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
    def get_check_dict(cls, view: model_views.PropertyView) -> dict[ClassCode, PsetDict]:
        return None


