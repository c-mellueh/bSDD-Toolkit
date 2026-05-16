"""UC/MS overlay for the property picker, backed by the Loin tool.

This module exposes:

* :class:`UcMsColumnProxy` — wraps a source model and appends one checkable
  column per (Purpose × Milestone) pair. Check state is *not* stored in the
  proxy; every read/write delegates to :class:`bsdd_gui.tool.PropertyPicker`.
* :class:`TwoRowHeaderView` — paints UC (top row) and MS (bottom row) headers
  derived from the Loin tool.
* :class:`FilterTableWindow` — a stand-alone editor for the UC/MS grid plus
  the global Providing/Receiving actor pair.
* :func:`get_filter_window` — singleton accessor used by the property picker.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    QRect,
    Qt,
    QTimer,
)
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from bsdd_gui import tool
from bsdd_json import BsddClass, BsddClassProperty
from bsdd_json.utils import class_utils
if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_root_classes():
    rc = class_utils.get_root_classes(tool.Project.get())
    return [c for c in rc if c.ClassType != "GroupOfProperties" and tool.PropertyPicker.is_class_added(c)]

def _get_children(bsdd_class: BsddClass):
    children = class_utils.get_children(bsdd_class)
    return [c for c in children if c.ClassType != "GroupOfProperties" and tool.PropertyPicker.is_class_added(c)]


def _current_purposes() -> list:
    return tool.PropertyPicker.get_purposes()


def _current_milestones() -> list:
    return tool.PropertyPicker.get_milestones()




def _column_to_guids(column: int, prefix_cols: int) -> Optional[tuple[UUID, UUID]]:
    """Return the (purpose_guid, milestone_guid) for a proxy column index."""
    if column < prefix_cols:
        return None
    purposes = _current_purposes()
    milestones = _current_milestones()
    if not purposes or not milestones:
        return None
    rel = column - prefix_cols
    num_ms = len(milestones)
    purpose_idx, milestone_idx = divmod(rel, num_ms)
    if purpose_idx >= len(purposes) or milestone_idx >= num_ms:
        return None
    return purposes[purpose_idx].guid, milestones[milestone_idx].guid


# ---------------------------------------------------------------------------
# Column proxy — adds UC × MS checkbox columns to any tree model
# ---------------------------------------------------------------------------


class ClassModel(QAbstractItemModel):
    """Wraps a source model and appends `len(uc) * len(ms)` checkable columns.

    State storage is delegated to the Loin tool — the proxy is now purely a
    view layer with no hidden booleans.
    """

    def __init__(self, prefix_cols: int = 2, parent=None):
        super().__init__(parent)
        self._prefix_cols = prefix_cols
        self._tracked_views: list[QTreeView] = []

        # loin_reset wipes everything — full model reset is correct there.
        # All other structural signals preserve expansion state so the tree
        # does not collapse when adding/removing purposes, milestones or classes.
        signals = tool.PropertyPicker.get_signals()
        signals.added_classes_changed.connect(self._reset_preserving_expansion)
        signals.purposes_changed.connect(self._reset_preserving_expansion)
        signals.milestones_changed.connect(self._reset_preserving_expansion)
        signals.loin_reset.connect(self._reset_view)

    def register_view(self, view: QTreeView) -> None:
        if view not in self._tracked_views:
            self._tracked_views.append(view)

    # ------------------------------------------------------------------ basics

    def _reset_view(self) -> None:
        self.beginResetModel()
        self.endResetModel()

    def _collect_expanded(self, view: QTreeView) -> set[str]:
        expanded: set[str] = set()

        def walk(parent_idx: QModelIndex) -> None:
            for row in range(self.rowCount(parent_idx)):
                idx = self.index(row, 0, parent_idx)
                if not idx.isValid():
                    continue
                if view.isExpanded(idx):
                    node = idx.internalPointer()
                    if node is not None and hasattr(node, "Code"):
                        expanded.add(node.Code)
                    walk(idx)

        walk(QModelIndex())
        return expanded

    def _apply_expanded(self, view: QTreeView, expanded: set[str]) -> None:
        if not expanded:
            return

        def walk(parent_idx: QModelIndex) -> None:
            for row in range(self.rowCount(parent_idx)):
                idx = self.index(row, 0, parent_idx)
                if not idx.isValid():
                    continue
                node = idx.internalPointer()
                if node is not None and hasattr(node, "Code") and node.Code in expanded:
                    view.setExpanded(idx, True)
                    walk(idx)

        walk(QModelIndex())

    def _reset_preserving_expansion(self) -> None:
        snapshots = [(v, self._collect_expanded(v)) for v in self._tracked_views]
        self.beginResetModel()
        self.endResetModel()
        for view, expanded in snapshots:
            self._apply_expanded(view, expanded)

    def setSourceModel(self, model) -> None:
        super().setSourceModel(model)
        if model:
            model.modelReset.connect(self._on_source_reset)

    # ------------------------------------------------------------------ column count

    def rowCount(self, /, parent = QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return 0
        if not parent.isValid():
            return len(_get_root_classes())
        parent_class: BsddClass = parent.internalPointer()
        return len(_get_children(parent_class))

    def columnCount(self, _parent=QModelIndex()) -> int:
        return self._prefix_cols + len(_current_purposes()) * len(_current_milestones())

    def parent(self,index:QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        node: BsddClass = index.internalPointer()
        if not node.ParentClassCode:
            return QModelIndex()  # root hat keinen Parent

        parent_cls = class_utils.get_class_by_code(tool.Project.get(), node.ParentClassCode)
        if parent_cls is None:
            return QModelIndex()

        # Geschwister des Elterns ermitteln – exakt wie in index():
        gp_code = parent_cls.ParentClassCode
        if gp_code:
            gp_cls = class_utils.get_class_by_code(tool.Project.get(), gp_code)
            siblings = (
                _get_children(gp_cls) if gp_cls is not None else _get_root_classes()
            )
        else:
            siblings = _get_root_classes()

        try:
            row = siblings.index(parent_cls)
        except ValueError:
            return QModelIndex()

        return self.createIndex(row, 0, parent_cls)

    # ------------------------------------------------------------------ index/parent

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        if not parent.isValid():
            roots = _get_root_classes()
            if 0 <= row < len(roots):
                return self.createIndex(row, column, roots[row])
            return QModelIndex()
        parent = parent.siblingAtColumn(0)  # optional, schadet nicht
        parent_class: BsddClass = parent.internalPointer()
        children = _get_children(parent_class)
        if 0 <= row < len(children):
            return self.createIndex(row, column, children[row])
        return QModelIndex()


    def _row_payload(self, index: QModelIndex):
        return index.internalPointer()

    # ------------------------------------------------------------------ data/flags

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        col = index.column()
        if role == Qt.ItemDataRole.CheckStateRole:
            if col < self._prefix_cols:
                return None
            else:
                return self._check_state(index)

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return index.internalPointer().Name
            if index.column() == 1:
                return index.internalPointer().Code
        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:
        col = index.column()
        if col >= self._prefix_cols and role == Qt.ItemDataRole.CheckStateRole:
            pm = _column_to_guids(col, self._prefix_cols)
            if pm is None:
                return False
            payload = index.internalPointer()
            included = Qt.CheckState(value) == Qt.CheckState.Checked
            if isinstance(payload, BsddClass):
                tool.PropertyPicker.set_class_included(payload, pm[0], pm[1], included)
            elif isinstance(payload, BsddClassProperty):
                # The property view nests properties under a pset string; the
                # underlying class is held on the source model.
                bsdd_class = self._owning_class_for_property_view(index)
                if bsdd_class is None:
                    return False
                tool.PropertyPicker.set_property_included(
                    bsdd_class, payload, pm[0], pm[1], included
                )
            else:
                return False
            self.dataChanged.emit(index, index, [role])
            return True
        return super().setData(index, value, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        col = index.column()
        if col >= self._prefix_cols:
            payload = index.internalPointer()
            if not isinstance(payload, (BsddClass, BsddClassProperty)):
                # Pset header rows in the property view are non-interactive.
                return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
        else:
            return         (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
            )


    # ------------------------------------------------------------------ state lookups

    def _check_state(self, index: QModelIndex) -> Qt.CheckState:
        pm = _column_to_guids(index.column(), self._prefix_cols)
        if pm is None:
            return Qt.CheckState.Unchecked
        payload = index.internalPointer()
        if isinstance(payload, BsddClass):
            return (
                Qt.CheckState.Checked
                if tool.PropertyPicker.is_class_included(payload, pm[0], pm[1])
                else Qt.CheckState.Unchecked
            )
        if isinstance(payload, BsddClassProperty):
            bsdd_class = self._owning_class_for_property_view(index)
            if bsdd_class is None:
                return Qt.CheckState.Unchecked
            return (
                Qt.CheckState.Checked
                if tool.PropertyPicker.is_property_included(bsdd_class, payload, pm[0], pm[1])
                else Qt.CheckState.Unchecked
            )
        return Qt.CheckState.Unchecked

    def _owning_class_for_property_view(self, index: QModelIndex) -> Optional[BsddClass]:
        """For the property view, return the bSDD class the model is bound to."""
        sm = self.sourceModel()
        # PropertyTreeModel stores it in .bsdd_data.
        bsdd_data = getattr(sm, "bsdd_data", None)
        if isinstance(bsdd_data, BsddClass):
            return bsdd_data
        # Some wrapped source models expose .sourceModel() (QSortFilterProxyModel).
        inner = getattr(sm, "sourceModel", None)
        if callable(inner):
            inner_model = inner()
            return getattr(inner_model, "bsdd_data", None)
        return None


# ---------------------------------------------------------------------------
# Two-row header
# ---------------------------------------------------------------------------


class TwoRowHeaderView(QHeaderView):
    TOP_H = 24
    _PADDING = 16

    def __init__(self, orientation, prefix_cols: int = 2, parent=None):
        super().__init__(orientation, parent)
        self._prefix_cols = prefix_cols
        self.setDefaultSectionSize(70)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.sectionResized.connect(lambda *_: self.viewport().update())

        signals = tool.PropertyPicker.get_signals()
        signals.purposes_changed.connect(self._on_loin_changed)
        signals.milestones_changed.connect(self._on_loin_changed)
        signals.loin_reset.connect(self._on_loin_changed)

    def _on_loin_changed(self) -> None:
        self.updateGeometry()
        self.viewport().update()

    def _bot_height(self) -> int:
        fm = self.fontMetrics()
        milestones = _current_milestones()
        if not milestones:
            return self._PADDING
        return (
            max(
                fm.horizontalAdvance(tool.PropertyPicker.milestone_display_name(m))
                for m in milestones
            )
            + self._PADDING
        )

    def sizeHint(self):
        hint = super().sizeHint()
        hint.setHeight(self.TOP_H + self._bot_height())
        return hint

    def paintSection(self, *_) -> None:
        pass

    def paintEvent(self, *_) -> None:
        painter = QPainter(self.viewport())
        painter.save()

        bot_h = self._bot_height()
        total_h = self.TOP_H + bot_h
        painter.fillRect(0, 0, self.viewport().width(), total_h, self.palette().button())

        bold = QFont(painter.font())
        bold.setBold(True)

        # Prefix columns (e.g. Name, Code) span both header rows.
        x = -self.offset()
        for col in range(self._prefix_cols):
            w = self.sectionSize(col)
            label = ""
            if self.model():
                label = self.model().headerData(
                    col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
                ) or ""
            self._draw_cell(painter, x, 0, w, total_h, str(label), bold)
            x += w

        purposes = _current_purposes()
        milestones = _current_milestones()
        num_ms = len(milestones)
        for ui_idx, purpose in enumerate(purposes):
            first_col = self._prefix_cols + ui_idx * num_ms
            x_uc = sum(self.sectionSize(c) for c in range(first_col)) - self.offset()
            w_uc = sum(self.sectionSize(first_col + m) for m in range(num_ms))
            uc_name = tool.PropertyPicker.purpose_display_name(purpose)
            self._draw_cell(painter, x_uc, 0, w_uc, self.TOP_H, uc_name, bold)

            x_ms = x_uc
            for mi, milestone in enumerate(milestones):
                w_ms = self.sectionSize(first_col + mi)
                ms_name = tool.PropertyPicker.milestone_display_name(milestone)
                self._draw_cell(painter, x_ms, self.TOP_H, w_ms, bot_h, ms_name, rotated=True)
                x_ms += w_ms

        painter.restore()

    def _draw_cell(
        self,
        painter: QPainter,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str,
        font: QFont | None = None,
        rotated: bool = False,
    ) -> None:
        rect = QRect(x, y, w, h)
        painter.setPen(self.palette().mid().color())
        painter.drawRect(rect.adjusted(0, 0, -1, -1))
        painter.setPen(self.palette().buttonText().color())
        if font:
            old = painter.font()
            painter.setFont(font)
        if rotated:
            painter.save()
            painter.translate(x + w / 2, y + h / 2)
            painter.rotate(-90)
            painter.drawText(QRect(-h // 2, -w // 2, h, w), Qt.AlignmentFlag.AlignCenter, text)
            painter.restore()
        else:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        if font:
            painter.setFont(old)


# ---------------------------------------------------------------------------
# Filter table window — UC/MS editor + global actors
# ---------------------------------------------------------------------------


class FilterTableWindow(QWidget):
    """Editor for the UC/MS grid plus the global Providing/Receiving actors.

    Add/remove/rename actions mutate the Loin tool directly; the registered
    tree views refresh themselves via the Loin signals.
    """

    def __init__(self, prefix_cols: int = 2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Use Cases / Milestones")
        self.setWindowFlags(Qt.WindowType.Window)
        self._prefix_cols = prefix_cols
        self._views: list[QTreeView] = []
        self._filter_table: QTableWidget | None = None

        layout = QVBoxLayout(self)
        self._table_holder = QWidget(self)
        self._table_layout = QVBoxLayout(self._table_holder)
        self._table_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._table_holder)
        layout.addWidget(self._build_actors_panel())

        self._rebuild_table()

        signals = tool.PropertyPicker.get_signals()
        signals.purposes_changed.connect(self._rebuild_table)
        signals.milestones_changed.connect(self._rebuild_table)
        signals.loin_reset.connect(self._rebuild_table)
        signals.actors_changed.connect(self._refresh_actor_fields)

    # ------------------------------------------------------------------ register

    def register_view(self, view: QTreeView) -> None:
        if view not in self._views:
            self._views.append(view)

    def unregister_view(self, view: QTreeView) -> None:
        self._views = [v for v in self._views if v is not view]

    # ------------------------------------------------------------------ table

    def _build_table(self) -> QTableWidget:
        purposes = _current_purposes()
        milestones = _current_milestones()
        table = QTableWidget(len(purposes), len(milestones))
        table.setVerticalHeaderLabels(
            [tool.PropertyPicker.purpose_display_name(p) for p in purposes]
        )
        table.setHorizontalHeaderLabels(
            [tool.PropertyPicker.milestone_display_name(m) for m in milestones]
        )
        table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        for ui_idx in range(len(purposes)):
            for mi in range(len(milestones)):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Checked)
                table.setItem(ui_idx, mi, item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setFixedHeight(
            table.horizontalHeader().height()
            + sum(table.rowHeight(r) for r in range(max(len(purposes), 1)))
            + 4
        )
        table.itemChanged.connect(self._on_filter_changed)

        vh = table.verticalHeader()
        vh.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        vh.customContextMenuRequested.connect(self._uc_context_menu)

        hh = table.horizontalHeader()
        hh.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        hh.customContextMenuRequested.connect(self._ms_context_menu)

        self._filter_table = table
        return table

    def _rebuild_table(self) -> None:
        # Clear the holder.
        while self._table_layout.count():
            item = self._table_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._table_layout.addWidget(self._build_table())
        self._sync_all_views()

    def _on_filter_changed(self, item: QTableWidgetItem) -> None:
        purposes = _current_purposes()
        milestones = _current_milestones()
        if not purposes or not milestones:
            return
        col = self._prefix_cols + item.row() * len(milestones) + item.column()
        hidden = item.checkState() != Qt.CheckState.Checked
        for view in self._views:
            view.setColumnHidden(col, hidden)
            view.header().viewport().update()

    def _sync_all_views(self) -> None:
        purposes = _current_purposes()
        milestones = _current_milestones()
        end = self._prefix_cols + len(purposes) * len(milestones)
        for view in self._views:
            for col in range(self._prefix_cols, end):
                view.setColumnHidden(col, False)
            view.header().viewport().update()

    # ------------------------------------------------------------------ context menus

    def _ask_name(self, prompt: str) -> str | None:
        name, ok = QInputDialog.getText(self, "Name", prompt)
        return name.strip() if ok and name.strip() else None

    def _uc_context_menu(self, pos) -> None:
        idx = self._filter_table.verticalHeader().logicalIndexAt(pos)
        purposes = _current_purposes()
        menu = QMenu(self)
        menu.addAction("Add Use Case", lambda: self._add_uc())
        if 0 <= idx < len(purposes):
            label = tool.PropertyPicker.purpose_display_name(purposes[idx])
            menu.addSeparator()
            menu.addAction(f"Rename '{label}'", lambda: self._rename_uc(purposes[idx].guid))
            menu.addAction(f"Remove '{label}'", lambda: self._remove_uc(purposes[idx].guid))
        menu.exec(self._filter_table.verticalHeader().mapToGlobal(pos))

    def _ms_context_menu(self, pos) -> None:
        idx = self._filter_table.horizontalHeader().logicalIndexAt(pos)
        milestones = _current_milestones()
        menu = QMenu(self)
        menu.addAction("Add Milestone", lambda: self._add_ms())
        if 0 <= idx < len(milestones):
            label = tool.PropertyPicker.milestone_display_name(milestones[idx])
            menu.addSeparator()
            menu.addAction(
                f"Rename '{label}'",
                lambda: self._rename_ms(milestones[idx].guid),
            )
            menu.addAction(
                f"Remove '{label}'",
                lambda: self._remove_ms(milestones[idx].guid),
            )
        menu.exec(self._filter_table.horizontalHeader().mapToGlobal(pos))

    def _add_uc(self) -> None:
        name = self._ask_name("Use case name:")
        if name:
            tool.PropertyPicker.add_purpose(name)

    def _add_ms(self) -> None:
        name = self._ask_name("Milestone name:")
        if name:
            tool.PropertyPicker.add_milestone(name)

    def _remove_uc(self, guid: UUID) -> None:
        tool.PropertyPicker.remove_purpose(guid)

    def _remove_ms(self, guid: UUID) -> None:
        tool.PropertyPicker.remove_milestone(guid)

    def _rename_uc(self, guid: UUID) -> None:
        new = self._ask_name("Use case name:")
        if new:
            tool.PropertyPicker.rename_purpose(guid, new)

    def _rename_ms(self, guid: UUID) -> None:
        new = self._ask_name("Milestone name:")
        if new:
            tool.PropertyPicker.rename_milestone(guid, new)

    # ------------------------------------------------------------------ actors panel

    def _build_actors_panel(self) -> QGroupBox:
        box = QGroupBox("Actors (Providing / Receiving)", self)
        outer = QVBoxLayout(box)

        self._le_prov_role = QLineEdit(box)
        self._le_prov_aff = QLineEdit(box)
        self._le_prov_email = QLineEdit(box)
        self._le_recv_role = QLineEdit(box)
        self._le_recv_aff = QLineEdit(box)
        self._le_recv_email = QLineEdit(box)

        for w in (self._le_prov_role, self._le_recv_role):
            w.setPlaceholderText("Role (required)")
        for w in (self._le_prov_aff, self._le_recv_aff):
            w.setPlaceholderText("Affiliation")
        for w in (self._le_prov_email, self._le_recv_email):
            w.setPlaceholderText("Email")

        rows = QHBoxLayout()
        for label, role, aff, email in (
            ("Providing", self._le_prov_role, self._le_prov_aff, self._le_prov_email),
            ("Receiving", self._le_recv_role, self._le_recv_aff, self._le_recv_email),
        ):
            col = QFormLayout()
            col.addRow(QLabel(f"<b>{label}</b>"))
            col.addRow("Role", role)
            col.addRow("Affiliation", aff)
            col.addRow("Email", email)
            wrapper = QWidget(box)
            wrapper.setLayout(col)
            rows.addWidget(wrapper)
        outer.addLayout(rows)

        for w in (
            self._le_prov_role,
            self._le_prov_aff,
            self._le_prov_email,
            self._le_recv_role,
            self._le_recv_aff,
            self._le_recv_email,
        ):
            w.editingFinished.connect(self._apply_actor_fields)

        return box

    def _refresh_actor_fields(self) -> None:
        prov = tool.PropertyPicker.get_providing_actor()
        recv = tool.PropertyPicker.get_receiving_actor()
        if prov is not None:
            self._le_prov_role.setText(prov.role.text if prov.role else "")
            self._le_prov_aff.setText(prov.affiliation or "")
            self._le_prov_email.setText(prov.email_address or "")
        if recv is not None:
            self._le_recv_role.setText(recv.role.text if recv.role else "")
            self._le_recv_aff.setText(recv.affiliation or "")
            self._le_recv_email.setText(recv.email_address or "")

    def _apply_actor_fields(self) -> None:
        prov_role = self._le_prov_role.text().strip()
        recv_role = self._le_recv_role.text().strip()
        if prov_role:
            tool.PropertyPicker.set_providing_actor(
                role=prov_role,
                affiliation=self._le_prov_aff.text().strip() or None,
                email_address=self._le_prov_email.text().strip() or None,
            )
        if recv_role:
            tool.PropertyPicker.set_receiving_actor(
                role=recv_role,
                affiliation=self._le_recv_aff.text().strip() or None,
                email_address=self._le_recv_email.text().strip() or None,
            )


# ---------------------------------------------------------------------------
# Shared singleton window
# ---------------------------------------------------------------------------

_window: FilterTableWindow | None = None


def get_filter_window() -> FilterTableWindow:
    global _window
    if _window is None:
        _window = FilterTableWindow(prefix_cols=2)
    return _window


def reset_filter_window() -> None:
    """Reset the cached singleton (used when the LOIN model is wiped)."""
    global _window
    if _window is not None:
        _window.close()
        _window.deleteLater()
        _window = None
