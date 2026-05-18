import sys
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QRect, QTimer
from PySide6.QtGui import QPainter, QFont
from PySide6.QtWidgets import (
    QApplication,
    QTreeView,
    QWidget,
    QVBoxLayout,
    QHeaderView,
    QStyleOptionButton,
    QStyle,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QMenu,
    QInputDialog,
)

USE_CASES: list[str] = ["UC 1", "UC 2", "UC 3"]
MILESTONES: list[str] = ["MSaaaaaaaaaaa 1", "MS 2", "MS 3", "MS 4"]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


class TreeNode:
    def __init__(self, name: str, num_cols: int = 0, parent: "TreeNode | None" = None):
        self.name = name
        self.parent = parent
        self.children: list["TreeNode"] = []
        self.checked = [Qt.CheckState.Unchecked] * num_cols

    def append_child(self, child: "TreeNode") -> "TreeNode":
        child.parent = self
        self.children.append(child)
        return child

    def child(self, row: int) -> "TreeNode":
        return self.children[row]

    def child_count(self) -> int:
        return len(self.children)

    def row(self) -> int:
        return self.parent.children.index(self) if self.parent else 0


def build_sample_data(num_cols: int) -> TreeNode:
    root = TreeNode("root", num_cols)
    for i in range(1, 4):
        item = root.append_child(TreeNode(f"Item {i}", num_cols))
        for j in range(1, 3):
            sub = item.append_child(TreeNode(f"Sub-item {i}.{j}", num_cols))
            for k in range(1, 3):
                sub.append_child(TreeNode(f"Sub-sub {i}.{j}.{k}", num_cols))
    return root


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class CheckboxTreeModel(QAbstractItemModel):
    def __init__(
        self,
        root: TreeNode,
        use_cases: list[str],
        milestones: list[str],
        parent=None,
    ):
        super().__init__(parent)
        self._root = root
        self._uc = use_cases
        self._ms = milestones

    # helpers

    def _num_cols(self) -> int:
        return len(self._uc) * len(self._ms)

    def _data_col(self, uc_idx: int, ms_idx: int) -> int:
        return uc_idx * len(self._ms) + ms_idx

    def _save_state(self) -> dict:
        out: dict = {}
        self._walk_save(self._root, out)
        return out

    def _walk_save(self, node: TreeNode, out: dict) -> None:
        for ui, uc in enumerate(self._uc):
            for mi, ms in enumerate(self._ms):
                out[(node.name, uc, ms)] = node.checked[self._data_col(ui, mi)]
        for child in node.children:
            self._walk_save(child, out)

    def _restore_state(self, node: TreeNode, saved: dict) -> None:
        node.checked = [Qt.CheckState.Unchecked] * self._num_cols()
        for ui, uc in enumerate(self._uc):
            for mi, ms in enumerate(self._ms):
                key = (node.name, uc, ms)
                if key in saved:
                    node.checked[self._data_col(ui, mi)] = saved[key]
        for child in node.children:
            self._restore_state(child, saved)

    def _reset_with(self, mutate_fn) -> None:
        saved = self._save_state()
        mutate_fn()
        self.beginResetModel()
        self._restore_state(self._root, saved)
        self.endResetModel()

    # public mutation API

    def add_use_case(self, idx: int, name: str) -> None:
        self._reset_with(lambda: self._uc.insert(idx, name))

    def remove_use_case(self, idx: int) -> None:
        self._reset_with(lambda: self._uc.pop(idx))

    def add_milestone(self, idx: int, name: str) -> None:
        self._reset_with(lambda: self._ms.insert(idx, name))

    def remove_milestone(self, idx: int) -> None:
        self._reset_with(lambda: self._ms.pop(idx))

    def reorder_use_cases(self, new_order: list[str]) -> None:
        self._reset_with(lambda: self._uc.__setitem__(slice(None), new_order))

    def reorder_milestones(self, new_order: list[str]) -> None:
        self._reset_with(lambda: self._ms.__setitem__(slice(None), new_order))

    # QAbstractItemModel interface

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_node = parent.internalPointer() if parent.isValid() else self._root
        return self.createIndex(row, column, parent_node.child(row))

    def parent(self, index=QModelIndex()):
        if not index.isValid():
            return QModelIndex()
        node: TreeNode = index.internalPointer()
        p = node.parent
        if p is self._root or p is None:
            return QModelIndex()
        return self.createIndex(p.row(), 0, p)

    def rowCount(self, parent=QModelIndex()):
        node = parent.internalPointer() if parent.isValid() else self._root
        return node.child_count()

    def columnCount(self, _parent=QModelIndex()):
        return 1 + self._num_cols()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        node: TreeNode = index.internalPointer()
        col = index.column()
        if col == 0:
            if role == Qt.ItemDataRole.DisplayRole:
                return node.name
        elif role == Qt.ItemDataRole.CheckStateRole:
            return node.checked[col - 1]
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        node: TreeNode = index.internalPointer()
        col = index.column()
        if col > 0 and role == Qt.ItemDataRole.CheckStateRole:
            node.checked[col - 1] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        base = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() > 0:
            base |= Qt.ItemFlag.ItemIsUserCheckable
        return base

    def headerData(self, _section, _orientation, _role=Qt.ItemDataRole.DisplayRole):
        return None


# ---------------------------------------------------------------------------
# Header view (two rows)
# ---------------------------------------------------------------------------


class TwoRowHeaderView(QHeaderView):
    TOP_H = 24
    _PADDING = 16

    def __init__(self, orientation, use_cases: list[str], milestones: list[str], parent=None):
        super().__init__(orientation, parent)
        self._uc = use_cases
        self._ms = milestones
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

    def paintSection(self, _painter, _rect, _logical_index):
        pass  # everything drawn in paintEvent

    def paintEvent(self, _event):
        painter = QPainter(self.viewport())
        painter.save()

        bot_h = self._bot_height()
        total_h = self.TOP_H + bot_h
        painter.fillRect(0, 0, self.viewport().width(), total_h, self.palette().button())

        bold = QFont(painter.font())
        bold.setBold(True)

        self._draw_cell(painter, -self.offset(), 0, self.sectionSize(0), total_h, "Name", bold)

        num_ms = len(self._ms)
        for ui, uc_name in enumerate(self._uc):
            first_col = 1 + ui * num_ms
            x_uc = sum(self.sectionSize(c) for c in range(first_col)) - self.offset()
            w_uc = sum(self.sectionSize(first_col + m) for m in range(num_ms))
            self._draw_cell(painter, x_uc, 0, w_uc, self.TOP_H, uc_name, bold)

            x_ms = x_uc
            for mi, ms_name in enumerate(self._ms):
                w_ms = self.sectionSize(first_col + mi)
                self._draw_cell(painter, x_ms, self.TOP_H, w_ms, bot_h, ms_name, rotated=True)
                x_ms += w_ms

        painter.restore()

    def _draw_cell(self, painter: QPainter, x, y, w, h, text, font=None, rotated=False):
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
# Delegate
# ---------------------------------------------------------------------------


class CheckboxDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        state = index.data(Qt.ItemDataRole.CheckStateRole)
        if state is None:
            super().paint(painter, option, index)
            return
        opt = QStyleOptionButton()
        opt.rect = option.rect
        opt.state = QStyle.StateFlag.State_Enabled | (
            QStyle.StateFlag.State_On
            if state == Qt.CheckState.Checked
            else QStyle.StateFlag.State_Off
        )
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_CheckBox, opt, painter)

    def editorEvent(self, event, model, option, index):
        if event.type() in (event.Type.MouseButtonRelease, event.Type.MouseButtonDblClick):
            current = index.data(Qt.ItemDataRole.CheckStateRole)
            new_state = (
                Qt.CheckState.Unchecked
                if current == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            model.setData(index, new_state, Qt.ItemDataRole.CheckStateRole)
            return True
        return super().editorEvent(event, model, option, index)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UC / MS Checkbox Tree")
        self.resize(1000, 600)

        self._uc = list(USE_CASES)
        self._ms = list(MILESTONES)

        self._model = CheckboxTreeModel(
            build_sample_data(len(self._uc) * len(self._ms)),
            self._uc,
            self._ms,
        )
        self._header = TwoRowHeaderView(Qt.Orientation.Horizontal, self._uc, self._ms)
        self._delegate = CheckboxDelegate()
        self._filter_table: QTableWidget | None = None

        self._tree = QTreeView()
        self._tree.setHeader(self._header)
        self._tree.setModel(self._model)
        self._apply_delegates()
        self._tree.expandAll()
        self._apply_column_widths()

        layout = QVBoxLayout(self)
        layout.addWidget(self._build_filter_table())
        layout.addWidget(self._tree)

        self._model.modelReset.connect(self._on_model_reset)

    # --- filter table ---

    def _build_filter_table(self) -> QTableWidget:
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

    def _rebuild_filter_table(self) -> None:
        layout = self.layout()
        old = layout.itemAt(0).widget()
        layout.removeWidget(old)
        old.deleteLater()
        layout.insertWidget(0, self._build_filter_table())

    def _on_filter_changed(self, item: QTableWidgetItem) -> None:
        col = 1 + item.row() * len(self._ms) + item.column()
        self._tree.setColumnHidden(col, item.checkState() != Qt.CheckState.Checked)
        self._header.viewport().update()

    # --- drag-to-reorder ---

    def _on_uc_moved(self, *_) -> None:
        vh = self._filter_table.verticalHeader()
        new_order = [self._uc[vh.logicalIndex(i)] for i in range(len(self._uc))]
        QTimer.singleShot(0, lambda: self._model.reorder_use_cases(new_order))

    def _on_ms_moved(self, *_) -> None:
        hh = self._filter_table.horizontalHeader()
        new_order = [self._ms[hh.logicalIndex(i)] for i in range(len(self._ms))]
        QTimer.singleShot(0, lambda: self._model.reorder_milestones(new_order))

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

    # --- mutations ---

    def _ask_name(self, prompt: str) -> str | None:
        name, ok = QInputDialog.getText(self, "Name", prompt)
        return name.strip() if ok and name.strip() else None

    def _add_uc(self, idx: int) -> None:
        name = self._ask_name("Use case name:")
        if name:
            self._model.add_use_case(idx, name)

    def _remove_uc(self, idx: int) -> None:
        self._model.remove_use_case(idx)

    def _add_ms(self, idx: int) -> None:
        name = self._ask_name("Milestone name:")
        if name:
            self._model.add_milestone(idx, name)

    def _remove_ms(self, idx: int) -> None:
        self._model.remove_milestone(idx)

    # --- post-reset sync ---

    def _on_model_reset(self) -> None:
        self._apply_delegates()
        self._apply_column_widths()
        self._tree.expandAll()
        self._header.updateGeometry()
        self._header.viewport().update()
        self._rebuild_filter_table()

    def _apply_delegates(self) -> None:
        for col in range(1, 1 + len(self._uc) * len(self._ms)):
            self._tree.setItemDelegateForColumn(col, self._delegate)

    def _apply_column_widths(self) -> None:
        self._tree.setColumnWidth(0, 150)
        for col in range(1, 1 + len(self._uc) * len(self._ms)):
            self._tree.setColumnWidth(col, 70)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
