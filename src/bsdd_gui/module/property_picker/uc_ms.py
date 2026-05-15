from __future__ import annotations

from PySide6.QtCore import Qt, QIdentityProxyModel, QModelIndex, QPersistentModelIndex, QRect, QTimer
from PySide6.QtGui import QPainter, QFont
from PySide6.QtWidgets import (
    QHeaderView, QInputDialog, QMenu, QSizePolicy,
    QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout, QWidget,
)

USE_CASES: list[str] = ["UC 1", "UC 2", "UC 3"]
MILESTONES: list[str] = ["MS 1", "MS 2", "MS 3", "MS 4"]


# ---------------------------------------------------------------------------
# Column proxy — adds UC × MS checkbox columns to any tree model
# ---------------------------------------------------------------------------

class UcMsColumnProxy(QIdentityProxyModel):
    """Wraps a source model and appends len(uc)*len(ms) checkable columns after prefix_cols.

    Every proxy index — prefix columns included — stores a QPersistentModelIndex pointing
    to (row, 0) in the source model as its internalPointer.  mapToSource always rebuilds
    the source index via sourceModel().index(), never via createIndex(), so it is safe
    when the source is a QSortFilterProxyModel.
    """

    def __init__(
        self,
        use_cases: list[str],
        milestones: list[str],
        prefix_cols: int = 2,
        parent=None,
    ):
        super().__init__(parent)
        self._uc = use_cases
        self._ms = milestones
        self._prefix_cols = prefix_cols
        self._pmi_alive: set[QPersistentModelIndex] = set()
        self._checked: dict[tuple[QPersistentModelIndex, int], Qt.CheckState] = {}

    def setSourceModel(self, model) -> None:
        super().setSourceModel(model)
        if model:
            model.modelReset.connect(self._on_source_reset)

    def _on_source_reset(self) -> None:
        self._pmi_alive.clear()
        self._checked.clear()

    def _intern(self, src_row0: QModelIndex) -> QPersistentModelIndex:
        pmi = QPersistentModelIndex(src_row0)
        self._pmi_alive.add(pmi)
        return pmi

    # --- column count ---

    def columnCount(self, _parent=QModelIndex()) -> int:
        if self.sourceModel() is None:
            return 0
        return self._prefix_cols + len(self._uc) * len(self._ms)

    # --- index / parent ---

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        sm = self.sourceModel()
        src_parent = self.mapToSource(parent)
        src_row0 = sm.index(row, 0, src_parent)
        if not src_row0.isValid():
            return QModelIndex()
        return self.createIndex(row, column, self._intern(src_row0))

    # --- source mapping ---

    def mapToSource(self, proxy_index: QModelIndex) -> QModelIndex:
        if not proxy_index.isValid():
            return QModelIndex()
        pmi = proxy_index.internalPointer()
        if not isinstance(pmi, QPersistentModelIndex) or not pmi.isValid():
            return QModelIndex()
        sm = self.sourceModel()
        src_row0 = QModelIndex(pmi)
        src_parent = sm.parent(src_row0)
        col = proxy_index.column() if proxy_index.column() < self._prefix_cols else 0
        return sm.index(src_row0.row(), col, src_parent)

    def mapFromSource(self, source_index: QModelIndex) -> QModelIndex:
        if not source_index.isValid():
            return QModelIndex()
        sm = self.sourceModel()
        src_parent = sm.parent(source_index)
        src_row0 = sm.index(source_index.row(), 0, src_parent)
        return self.createIndex(source_index.row(), source_index.column(), self._intern(src_row0))

    # --- data / flags ---

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        col = index.column()
        if col >= self._prefix_cols:
            if role == Qt.ItemDataRole.CheckStateRole:
                pmi = index.internalPointer()
                if isinstance(pmi, QPersistentModelIndex):
                    return self._checked.get((pmi, col), Qt.CheckState.Unchecked)
            return None
        return super().data(index, role)

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:
        col = index.column()
        if col >= self._prefix_cols and role == Qt.ItemDataRole.CheckStateRole:
            pmi = index.internalPointer()
            if isinstance(pmi, QPersistentModelIndex):
                self._checked[(pmi, col)] = value
                self.dataChanged.emit(index, index, [role])
                return True
        return super().setData(index, value, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        col = index.column()
        if col >= self._prefix_cols:
            return (Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsUserCheckable)
        src = self.mapToSource(index)
        if not src.isValid():
            return Qt.ItemFlag.NoItemFlags
        return self.sourceModel().flags(src)


# ---------------------------------------------------------------------------
# Two-row header
# ---------------------------------------------------------------------------

class TwoRowHeaderView(QHeaderView):
    TOP_H = 24
    _PADDING = 16

    def __init__(
        self,
        orientation,
        use_cases: list[str],
        milestones: list[str],
        prefix_cols: int = 2,
        parent=None,
    ):
        super().__init__(orientation, parent)
        self._uc = use_cases
        self._ms = milestones
        self._prefix_cols = prefix_cols
        self.setDefaultSectionSize(70)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.sectionResized.connect(lambda *_: self.viewport().update())

    def _bot_height(self) -> int:
        fm = self.fontMetrics()
        if not self._ms:
            return self._PADDING
        return max(fm.horizontalAdvance(ms) for ms in self._ms) + self._PADDING

    def sizeHint(self):
        hint = super().sizeHint()
        hint.setHeight(self.TOP_H + self._bot_height())
        return hint

    def paintSection(self, *_) -> None:
        pass  # all drawing happens in paintEvent

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

        num_ms = len(self._ms)
        for ui, uc_name in enumerate(self._uc):
            first_col = self._prefix_cols + ui * num_ms
            x_uc = sum(self.sectionSize(c) for c in range(first_col)) - self.offset()
            w_uc = sum(self.sectionSize(first_col + m) for m in range(num_ms))
            self._draw_cell(painter, x_uc, 0, w_uc, self.TOP_H, uc_name, bold)

            x_ms = x_uc
            for mi, ms_name in enumerate(self._ms):
                w_ms = self.sectionSize(first_col + mi)
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
# Filter table window
# ---------------------------------------------------------------------------

class FilterTableWindow(QWidget):
    """Standalone window that controls UC/MS column visibility in registered tree views."""

    def __init__(
        self,
        use_cases: list[str],
        milestones: list[str],
        prefix_cols: int = 2,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Edit Use Cases / Milestones")
        self.setWindowFlags(Qt.WindowType.Window)
        self._uc = use_cases
        self._ms = milestones
        self._prefix_cols = prefix_cols
        self._views: list[QTreeView] = []
        self._filter_table: QTableWidget | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(self._build_table())

    def register_view(self, view: QTreeView) -> None:
        if view not in self._views:
            self._views.append(view)

    def unregister_view(self, view: QTreeView) -> None:
        self._views = [v for v in self._views if v is not view]

    # --- table construction ---

    def _build_table(self) -> QTableWidget:
        table = QTableWidget(len(self._uc), len(self._ms))
        table.setVerticalHeaderLabels(self._uc)
        table.setHorizontalHeaderLabels(self._ms)
        table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        for ui in range(len(self._uc)):
            for mi in range(len(self._ms)):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Checked)
                table.setItem(ui, mi, item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setFixedHeight(
            table.horizontalHeader().height()
            + sum(table.rowHeight(r) for r in range(len(self._uc)))
            + 4
        )
        table.itemChanged.connect(self._on_filter_changed)

        vh = table.verticalHeader()
        vh.setSectionsMovable(True)
        vh.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        vh.customContextMenuRequested.connect(self._uc_context_menu)
        vh.sectionMoved.connect(self._on_uc_moved)

        hh = table.horizontalHeader()
        hh.setSectionsMovable(True)
        hh.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        hh.customContextMenuRequested.connect(self._ms_context_menu)
        hh.sectionMoved.connect(self._on_ms_moved)

        self._filter_table = table
        return table

    def _rebuild_table(self) -> None:
        layout = self.layout()
        old = layout.itemAt(0).widget()
        layout.removeWidget(old)
        old.deleteLater()
        layout.addWidget(self._build_table())
        self._sync_all_views()

    # --- filter changed ---

    def _on_filter_changed(self, item: QTableWidgetItem) -> None:
        col = self._prefix_cols + item.row() * len(self._ms) + item.column()
        hidden = item.checkState() != Qt.CheckState.Checked
        for view in self._views:
            view.setColumnHidden(col, hidden)
            view.header().viewport().update()

    def _sync_all_views(self) -> None:
        end = self._prefix_cols + len(self._uc) * len(self._ms)
        for view in self._views:
            for col in range(self._prefix_cols, end):
                view.setColumnHidden(col, False)
            view.header().viewport().update()

    def _refresh_headers(self) -> None:
        for view in self._views:
            view.header().updateGeometry()
            view.header().viewport().update()

    # --- drag-to-reorder ---

    def _on_uc_moved(self, *_) -> None:
        vh = self._filter_table.verticalHeader()
        new_order = [self._uc[vh.logicalIndex(i)] for i in range(len(self._uc))]
        QTimer.singleShot(0, lambda: self._apply_uc_reorder(new_order))

    def _on_ms_moved(self, *_) -> None:
        hh = self._filter_table.horizontalHeader()
        new_order = [self._ms[hh.logicalIndex(i)] for i in range(len(self._ms))]
        QTimer.singleShot(0, lambda: self._apply_ms_reorder(new_order))

    def _apply_uc_reorder(self, new_order: list[str]) -> None:
        self._uc[:] = new_order
        self._rebuild_table()
        self._refresh_headers()

    def _apply_ms_reorder(self, new_order: list[str]) -> None:
        self._ms[:] = new_order
        self._rebuild_table()
        self._refresh_headers()

    # --- context menus ---

    def _uc_context_menu(self, pos) -> None:
        idx = self._filter_table.verticalHeader().logicalIndexAt(pos)
        menu = QMenu(self)
        menu.addAction("Add Use Case above", lambda: self._add_uc(idx))
        menu.addAction("Add Use Case below", lambda: self._add_uc(idx + 1))
        if len(self._uc) > 1:
            menu.addSeparator()
            menu.addAction(f"Remove '{self._uc[idx]}'", lambda: self._remove_uc(idx))
        menu.exec(self._filter_table.verticalHeader().mapToGlobal(pos))

    def _ms_context_menu(self, pos) -> None:
        idx = self._filter_table.horizontalHeader().logicalIndexAt(pos)
        menu = QMenu(self)
        menu.addAction("Add Milestone before", lambda: self._add_ms(idx))
        menu.addAction("Add Milestone after", lambda: self._add_ms(idx + 1))
        if len(self._ms) > 1:
            menu.addSeparator()
            menu.addAction(f"Remove '{self._ms[idx]}'", lambda: self._remove_ms(idx))
        menu.exec(self._filter_table.horizontalHeader().mapToGlobal(pos))

    def _ask_name(self, prompt: str) -> str | None:
        name, ok = QInputDialog.getText(self, "Name", prompt)
        return name.strip() if ok and name.strip() else None

    def _add_uc(self, idx: int) -> None:
        name = self._ask_name("Use case name:")
        if not name:
            return
        self._uc.insert(idx, name)
        self._rebuild_table()
        self._refresh_headers()

    def _remove_uc(self, idx: int) -> None:
        self._uc.pop(idx)
        self._rebuild_table()
        self._refresh_headers()

    def _add_ms(self, idx: int) -> None:
        name = self._ask_name("Milestone name:")
        if not name:
            return
        self._ms.insert(idx, name)
        self._rebuild_table()
        self._refresh_headers()

    def _remove_ms(self, idx: int) -> None:
        self._ms.pop(idx)
        self._rebuild_table()
        self._refresh_headers()


# ---------------------------------------------------------------------------
# Shared singleton window
# ---------------------------------------------------------------------------

_window: FilterTableWindow | None = None


def get_filter_window() -> FilterTableWindow:
    global _window
    if _window is None:
        _window = FilterTableWindow(USE_CASES, MILESTONES, prefix_cols=2)
    return _window
