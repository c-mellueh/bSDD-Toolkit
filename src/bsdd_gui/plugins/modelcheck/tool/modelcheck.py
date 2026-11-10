import ifcopenshell
import ifcopenshell.util.element as ifc_el


class Modelcheck:
    @classmethod
    def extract_psets(cls, element: ifcopenshell.entity_instance) -> dict[str, dict]:
        try:
            return ifc_el.get_psets(element) or {}
        except Exception:
            return {}
