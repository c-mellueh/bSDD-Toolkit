import datetime
import re
from types import SimpleNamespace

import ifcopenshell

from bsdd_json.utils.property_utils import get_property_by_class_property
from bsdd_gui.plugins.modelcheck.module import constants


def extract_psets(element: ifcopenshell.entity_instance) -> dict[str, dict]:
    try:
        import ifcopenshell.util.element as ifc_el

        return ifc_el.get_psets(element) or {}
    except Exception:
        return {}


def _coerce_string(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        for key in ("NominalValue", "value", "Value", "wrappedValue"):
            if key in value:
                return _coerce_string(value[key])
        return str(value)
    return str(value)


def _allowed_values(prop) -> list[str]:
    allowed = getattr(prop, "AllowedValues", None) or []
    values: list[str] = []
    for item in allowed:
        if isinstance(item, dict):
            for key in ("Value", "value"):
                if key in item:
                    values.append(str(item[key]))
                    break
            else:
                values.append(str(next(iter(item.values()), "")))
        elif hasattr(item, "Value"):
            values.append(str(item.Value))
        else:
            values.append(str(item))
    return values


def check_format(value: str, prop) -> tuple[bool, str]:
    pattern = getattr(prop, "Pattern", None)
    if pattern:
        try:
            if not re.search(pattern, _coerce_string(value)):
                return False, f"Value '{value}' does not match pattern '{pattern}'"
        except Exception as exc:
            return False, f"Pattern check error: {exc}"
    return True, ""


def check_range(value, prop) -> tuple[bool, str]:
    try:
        num = float(value)
    except (ValueError, TypeError, AttributeError):
        return False, f"Value '{value}' cannot be converted to number for range check"

    min_inc = getattr(prop, "MinInclusive", None)
    max_inc = getattr(prop, "MaxInclusive", None)
    min_exc = getattr(prop, "MinExclusive", None)
    max_exc = getattr(prop, "MaxExclusive", None)

    if min_inc is not None and num < min_inc:
        return False, f"Value {num} is less than MinInclusive {min_inc}"
    if max_inc is not None and num > max_inc:
        return False, f"Value {num} is greater than MaxInclusive {max_inc}"
    if min_exc is not None and num <= min_exc:
        return False, f"Value {num} is less than or equal to MinExclusive {min_exc}"
    if max_exc is not None and num >= max_exc:
        return False, f"Value {num} is greater than or equal to MaxExclusive {max_exc}"

    return True, ""


def check_list(value, prop) -> tuple[bool, str]:
    allowed_vals = _allowed_values(prop)
    if not allowed_vals:
        return True, ""

    values = [value] if not isinstance(value, (list, tuple, set)) else list(value)
    normalized_values = [_coerce_string(v).strip() for v in values]
    normalized_allowed = [str(v).strip() for v in allowed_vals]

    for item in normalized_values:
        if item.lower() not in {allowed.lower() for allowed in normalized_allowed}:
            return False, f"Value '{value}' not in allowed values: {allowed_vals}"
    return True, ""


def check_datatype(value, expected_type: str) -> tuple[bool, str]:
    if not expected_type:
        return True, ""
    exp = str(expected_type).lower()

    if exp in {"string", "text", "label", "varchar", "char", "identifier", "uri"}:
        if isinstance(value, str):
            return True, ""
        if isinstance(value, (int, float, bool)):
            return True, ""
        return False, "Expected text/string"

    if exp in {"integer", "int"}:
        if isinstance(value, bool):
            return False, "Expected integer"
        if isinstance(value, int):
            return True, ""
        if isinstance(value, str):
            try:
                int(value)
                return True, ""
            except ValueError:
                return False, "Expected integer"
        return False, "Expected integer"

    if exp in {"real", "float", "number", "double", "decimal"}:
        if isinstance(value, bool):
            return False, "Expected real/number"
        if isinstance(value, (int, float)):
            return True, ""
        if isinstance(value, str):
            try:
                float(value)
                return True, ""
            except ValueError:
                return False, "Expected real/number"
        return False, "Expected real/number"

    if exp in {"boolean", "bool", "logical"}:
        if isinstance(value, bool):
            return True, ""
        if isinstance(value, str):
            lower = value.strip().lower()
            if lower in {"true", "false", "yes", "no", "1", "0"}:
                return True, ""
        return False, "Expected boolean"

    return True, ""


def check_element(element: ifcopenshell.entity_instance, bsdd_class, issues: list):
    guid = getattr(element, "GlobalId", "")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    psets = extract_psets(element)

    def _value_for(class_prop, pset_name):
        props_in_set = psets.get(pset_name, {})
        prop_code = getattr(class_prop, "PropertyCode", None)
        if prop_code is None:
            return None
        if prop_code in props_in_set:
            return props_in_set[prop_code]
        if not isinstance(props_in_set, dict):
            return None
        for key, value in props_in_set.items():
            if str(key).lower() == str(prop_code).lower():
                return value
        return None

    for class_prop in (getattr(bsdd_class, "ClassProperties", None) or []):
        pset_name = getattr(class_prop, "PropertySet", "") or "Common"
        prop_code = getattr(class_prop, "PropertyCode", "")
        is_required = getattr(class_prop, "IsRequired", False)

        if pset_name not in psets:
            if is_required:
                issues.append({
                    "GUID_ZWC": "",
                    "GUID": guid,
                    "creation_date": now_str,
                    "short_description": f"Missing PropertySet '{pset_name}'",
                    "issue_type": constants.PROPERTY_SET_ISSUE,
                    "PropertySet": pset_name,
                    "Property": prop_code,
                    "Value": "",
                    "ValueType": "",
                    "description": f"Required PropertySet '{pset_name}' not found on {element.is_a()}",
                })
            continue

        val = _value_for(class_prop, pset_name)
        if val is None:
            if is_required:
                issues.append({
                    "GUID_ZWC": "",
                    "GUID": guid,
                    "creation_date": now_str,
                    "short_description": f"Missing Property '{prop_code}'",
                    "issue_type": constants.PROPERTY_EXIST_ISSUE,
                    "PropertySet": pset_name,
                    "Property": prop_code,
                    "Value": "",
                    "ValueType": "",
                    "description": f"Required Property '{prop_code}' missing in PropertySet '{pset_name}'",
                })
            continue

        if val is None or val == "":
            if is_required:
                issues.append({
                    "GUID_ZWC": "",
                    "GUID": guid,
                    "creation_date": now_str,
                    "short_description": f"Empty value for '{prop_code}'",
                    "issue_type": constants.PROPERTY_VALUE_ISSUES,
                    "PropertySet": pset_name,
                    "Property": prop_code,
                    "Value": "",
                    "ValueType": "",
                    "description": f"Property '{prop_code}' in '{pset_name}' has an empty value",
                })
            continue

        prop_spec = None
        try:
            dict_obj = getattr(bsdd_class, "parent", lambda: None)()
            if dict_obj is not None:
                prop_spec = get_property_by_class_property(class_prop, dict_obj)
        except Exception:
            prop_spec = None

        rule_source = prop_spec or class_prop
        ok_dtype, dtype_msg = check_datatype(val, getattr(rule_source, "DataType", None))
        if not ok_dtype:
            issues.append({
                "GUID_ZWC": "",
                "GUID": guid,
                "creation_date": now_str,
                "short_description": f"Datatype violation on '{prop_code}'",
                "issue_type": constants.DATATYPE_ISSUE,
                "PropertySet": pset_name,
                "Property": prop_code,
                "Value": val,
                "ValueType": str(type(val).__name__),
                "description": dtype_msg,
            })

        ok_fmt, fmt_msg = check_format(val, rule_source)
        if not ok_fmt:
            issues.append({
                "GUID_ZWC": "",
                "GUID": guid,
                "creation_date": now_str,
                "short_description": f"Format violation on '{prop_code}'",
                "issue_type": constants.PROPERTY_VALUE_ISSUES,
                "PropertySet": pset_name,
                "Property": prop_code,
                "Value": val,
                "ValueType": str(type(val).__name__),
                "description": fmt_msg,
            })

        ok_range, range_msg = check_range(val, rule_source)
        if not ok_range:
            issues.append({
                "GUID_ZWC": "",
                "GUID": guid,
                "creation_date": now_str,
                "short_description": f"Range violation on '{prop_code}'",
                "issue_type": constants.PROPERTY_VALUE_ISSUES,
                "PropertySet": pset_name,
                "Property": prop_code,
                "Value": val,
                "ValueType": str(type(val).__name__),
                "description": range_msg,
            })

        ok_list, list_msg = check_list(val, rule_source)
        if not ok_list:
            issues.append({
                "GUID_ZWC": "",
                "GUID": guid,
                "creation_date": now_str,
                "short_description": f"Allowed values violation on '{prop_code}'",
                "issue_type": constants.PROPERTY_VALUE_ISSUES,
                "PropertySet": pset_name,
                "Property": prop_code,
                "Value": val,
                "ValueType": str(type(val).__name__),
                "description": list_msg,
            })
