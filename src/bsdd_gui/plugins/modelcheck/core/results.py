import os
import uuid
import zipfile
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from bsdd_gui.plugins.modelcheck.module import constants


def _bcf_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_bcf_report(issues: list[dict], export_path: str):
    export_dir = os.path.dirname(export_path) or "."
    os.makedirs(export_dir, exist_ok=True)

    ns = "http://www.buildingsmart.org/bcf/2.1"
    ET.register_namespace("", ns)
    root = ET.Element(f"{{{ns}}}Markup")

    for index, issue in enumerate(issues):
        topic = ET.SubElement(root, f"{{{ns}}}Topic")
        guid = str(issue.get("GUID") or issue.get("GUID_ZWC") or uuid.uuid4())
        ET.SubElement(topic, f"{{{ns}}}Guid").text = guid
        ET.SubElement(topic, f"{{{ns}}}Title").text = str(
            issue.get("short_description") or f"Modelcheck issue {index + 1}"
        )
        ET.SubElement(topic, f"{{{ns}}}Priority").text = "Normal"
        ET.SubElement(topic, f"{{{ns}}}Index").text = str(index)
        ET.SubElement(topic, f"{{{ns}}}CreationDate").text = str(
            issue.get("creation_date") or _bcf_timestamp()
        ).replace(" ", "T")
        ET.SubElement(topic, f"{{{ns}}}CreationAuthor").text = "bSDD-Toolkit"
        ET.SubElement(topic, f"{{{ns}}}ModifiedDate").text = _bcf_timestamp()
        ET.SubElement(topic, f"{{{ns}}}ModifiedAuthor").text = "bSDD-Toolkit"
        ET.SubElement(topic, f"{{{ns}}}Description").text = str(
            issue.get("description") or issue.get("short_description") or "No description"
        )
        ET.SubElement(topic, f"{{{ns}}}TopicType").text = "Modelcheck"
        ET.SubElement(topic, f"{{{ns}}}TopicStatus").text = "Open"

        labels = ET.SubElement(topic, f"{{{ns}}}Labels")
        for label in (
            issue.get("PropertySet"),
            issue.get("Property"),
            "Modelcheck",
        ):
            if label:
                label_node = ET.SubElement(labels, f"{{{ns}}}Label")
                label_node.text = str(label)

        comment = ET.SubElement(topic, f"{{{ns}}}Comment")
        comment.text = str(issue.get("description") or issue.get("short_description") or "")

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(export_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("bcf.version", "2.1")
        zf.writestr("markup.bcf", xml_bytes)


def create_excel_report(issues: list[dict], export_path: str):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Modelcheck Issues"

    headers = constants.ISSUE_TABLE_HEADER
    ws.append(headers)

    for issue in issues:
        row = [
            issue.get("GUID_ZWC", ""),
            issue.get("GUID", ""),
            issue.get("creation_date", ""),
            issue.get("short_description", ""),
            issue.get("issue_type", ""),
            issue.get("PropertySet", ""),
            issue.get("Property", ""),
            str(issue.get("Value", "")),
            str(issue.get("ValueType", "")),
            issue.get("description", ""),
        ]
        ws.append(row)

    row_count = max(len(issues) + 1, 2)
    col_count = len(headers)
    end_col = get_column_letter(col_count)
    table_ref = f"A1:{end_col}{row_count}"

    tab = Table(displayName="ModelcheckTable", ref=table_ref)
    style = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=True,
    )
    tab.tableStyleInfo = style
    ws.add_table(tab)

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(export_path)
