"""Excel export: one overview sheet plus one sheet per root class."""

from __future__ import annotations

import io
import re

import openpyxl
from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
from bsdd_json.utils import dictionary_utils as dict_utils
from openpyxl import Workbook, styles
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from .i18n import t
from .loin import Selection
from .resolve import resolver_for

COLUMN_COUNT = 6
MAX_ENTRIES = 8
TABLE_STYLE = "TableStyleLight1"
_ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_SHEET_INVALID = re.compile(r"[\\/*?:\[\]]")


def _clean(value):
    if isinstance(value, str):
        return _ILLEGAL.sub("", value)
    return value


class _Builder:
    def __init__(self, d: BsddDictionary, selection: Selection, lang: str):
        self.d = d
        self.sel = selection
        self.lang = lang
        self.resolve = resolver_for(d)
        self.table_names: set[str] = set()
        self.sheet_names: set[str] = set()
        self.children: dict[str | None, list[BsddClass]] = {}
        for c in d.Classes:
            self.children.setdefault(c.ParentClassCode, []).append(c)

    def table_name(self, name: str) -> str:
        base = dict_utils.slugify(name, delimiter="_") or "Table"
        base = re.sub(r"[^A-Za-z0-9_]", "_", base)
        if not re.match(r"[A-Za-z_]", base):
            base = f"T_{base}"
        base = base[:200]
        candidate, i = base, 2
        while candidate.lower() in self.table_names or re.fullmatch(r"[A-Za-z]{1,3}\d+", candidate):
            candidate = f"{base}_{i}"
            i += 1
        self.table_names.add(candidate.lower())
        return candidate

    def sheet_name(self, name: str) -> str:
        base = _SHEET_INVALID.sub("_", name or "Sheet").strip("'")[:31] or "Sheet"
        candidate, i = base, 2
        while candidate.lower() in self.sheet_names:
            suffix = f" ({i})"
            candidate = base[: 31 - len(suffix)] + suffix
            i += 1
        self.sheet_names.add(candidate.lower())
        return candidate

    def cell(self, sheet: Worksheet, row: int, col: int, value) -> None:
        sheet.cell(row, col, _clean(value))

    def draw_border(self, sheet: Worksheet, rows: tuple[int, int], cols: tuple[int, int]) -> None:
        thick = styles.Side(border_style="thick", color="FF000000")
        none = styles.Side(border_style=None)
        for r in range(rows[0], rows[1] + 1):
            for c in range(cols[0], cols[1] + 1):
                sheet.cell(r, c).border = styles.Border(
                    left=thick if c == cols[0] else none,
                    right=thick if c == cols[1] else none,
                    top=thick if r == rows[0] else none,
                    bottom=thick if r == rows[1] else none,
                )

    def fill_grey(self, sheet: Worksheet, rows: tuple[int, int], cols: tuple[int, int]) -> None:
        fill = styles.PatternFill(fill_type="solid", start_color="d9d9d9")
        for r in range(rows[0], rows[1] + 1):
            for c in range(cols[0], cols[1] + 1):
                sheet.cell(r, c).fill = fill

    def create_table(self, sheet: Worksheet, rows: tuple[int, int], cols: tuple[int, int], name: str) -> None:
        ref = f"{sheet.cell(rows[0], cols[0]).coordinate}:{sheet.cell(rows[1], cols[1]).coordinate}"
        table = Table(displayName=self.table_name(name), ref=ref)
        table.tableStyleInfo = TableStyleInfo(name=TABLE_STYLE, showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        sheet.add_table(table)

    def draw_class(self, c: BsddClass, row: int, col: int, sheet: Worksheet) -> int:
        lang = self.lang
        self.cell(sheet, row, col, t("Name", lang))
        self.cell(sheet, row, col + 1, c.Name)
        self.cell(sheet, row, col + 2, t("Parent Code", lang))
        self.cell(sheet, row, col + 3, c.ParentClassCode or "")
        self.cell(sheet, row + 1, col, t("Identifier", lang))
        self.cell(sheet, row + 1, col + 1, c.Code)
        self.cell(sheet, row + 2, col, t("Definition", lang))
        self.cell(sheet, row + 2, col + 1, c.Definition)
        headers = ["Property", "PropertySet", "Definition", "Datatype", "Values"]
        for i, h in enumerate(headers):
            self.cell(sheet, row + 3, col + i, t(h, lang))
        self.draw_border(sheet, (row, row + 2), (col, col + 4))
        self.fill_grey(sheet, (row, row + 2), (col, col + 4))
        start = row + 3
        props: list[BsddClassProperty] = sorted(
            (cp for cp in c.ClassProperties if self.sel.property_included(c, cp)),
            key=lambda cp: cp.PropertySet or "",
        )
        n = 0
        for n, cp in enumerate(props, start=1):
            prop = self.resolve.property(cp)
            values = cp.AllowedValues or (prop.AllowedValues if prop else [])
            self.cell(sheet, start + n, col, prop.Name if prop else cp.Code)
            self.cell(sheet, start + n, col + 1, cp.PropertySet)
            self.cell(sheet, start + n, col + 2, self.resolve.definition(cp))
            self.cell(sheet, start + n, col + 3, (prop.DataType if prop else None) or "IFCLABEL")
            self.cell(sheet, start + n, col + 4, "; ".join(v.Code for v in values))
        self.create_table(sheet, (start, start + n), (col, col + 4), c.Name)
        return start + n

    def descendants(self, c: BsddClass) -> list[BsddClass]:
        out: list[BsddClass] = []
        queue = list(self.children.get(c.Code, []))
        while queue:
            child = queue.pop(0)
            out.append(child)
            queue.extend(self.children.get(child.Code, []))
        return out

    def class_sheet(self, wb: Workbook, root: BsddClass) -> list[BsddClass]:
        sheet = wb.create_sheet(self.sheet_name(root.Name))
        row, col = 1, 1
        max_row = self.draw_class(root, row, col, sheet)
        exported = [root]
        items = 1
        col += COLUMN_COUNT
        for child in self.descendants(root):
            if not self.sel.class_included(child) or child.ClassType == "GroupOfProperties":
                continue
            exported.append(child)
            max_row = max(max_row, self.draw_class(child, row, col, sheet))
            col += COLUMN_COUNT
            items += 1
            if items >= MAX_ENTRIES:
                col, row, items = 1, max_row + 2, 0
        return exported

    def overview(self, sheet: Worksheet, classes: list[BsddClass]) -> None:
        sheet.title = self.sheet_name(t("Overview", self.lang))
        for i, h in enumerate(("Code", "Name", "Definition"), start=1):
            self.cell(sheet, 1, i, h)
        row = 1
        for row, c in enumerate(classes, start=2):
            self.cell(sheet, row, 1, c.Code.strip())
            self.cell(sheet, row, 2, c.Name.strip())
            self.cell(sheet, row, 3, c.Definition or "")
        if row == 1:
            row = 2
        self.create_table(sheet, (1, row), (1, 3), sheet.title)


def export_excel(d: BsddDictionary, selection: Selection, lang: str = "en") -> tuple[bytes, int]:
    """Return the xlsx bytes and the number of exported classes."""
    builder = _Builder(d, selection, lang)
    classes = [c for c in d.Classes if selection.class_included(c) and c.ClassType != "GroupOfProperties"]
    codes = {c.Code for c in classes}
    # a "root" is a selected class without a selected ancestor
    roots = []
    index = {c.Code: c for c in d.Classes}
    for c in classes:
        parent = c.ParentClassCode
        has_selected_ancestor = False
        seen = set()
        while parent and parent not in seen:
            seen.add(parent)
            if parent in codes:
                has_selected_ancestor = True
                break
            parent = index[parent].ParentClassCode if parent in index else None
        if not has_selected_ancestor:
            roots.append(c)
    wb = openpyxl.Workbook()
    overview = wb.active
    exported: list[BsddClass] = []
    for root in roots:
        exported.extend(builder.class_sheet(wb, root))
    builder.overview(overview, exported)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue(), len(exported)
