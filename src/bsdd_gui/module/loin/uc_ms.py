"""UC/MS overlay for the property picker, backed by the Loin tool.

This module exposes:

* :class:`UcMsColumnProxy` — wraps a source model and appends one checkable
  column per (Purpose × Milestone) pair. Check state is *not* stored in the
  proxy; every read/write delegates to :class:`bsdd_gui.tool.Loin`.
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
    QEvent,
    QModelIndex,
    QRect,
    Qt,
)
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionButton,
    QTableWidget,
    QTableWidgetItem,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from bsdd_gui import tool
from bsdd_json import BsddClass, BsddClassProperty
from bsdd_json.utils import class_utils
from bsdd_json.utils import property_utils as prop_utils

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_root_classes():
    rc = class_utils.get_root_classes(tool.Project.get())
    return [c for c in rc if c.ClassType != "GroupOfProperties" and tool.Loin.is_class_added(c)]


def _get_children(bsdd_class: BsddClass):
    children = class_utils.get_children(bsdd_class)
    return [
        c for c in children if c.ClassType != "GroupOfProperties" and tool.Loin.is_class_added(c)
    ]


def _current_purposes() -> list:
    return tool.Loin.get_purposes()


def _current_milestones() -> list:
    return tool.Loin.get_milestones()


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
# ---------------------------------------------------------------------------
# Centered-checkbox delegate for UC × MS columns
# ---------------------------------------------------------------------------


class _CenteredCheckDelegate(QStyledItemDelegate):
    """Draws the checkbox centred in its cell for columns that carry CheckStateRole."""

    def paint(self, painter, option, index) -> None:
        check = index.data(Qt.ItemDataRole.CheckStateRole)
        if check is None:
            super().paint(painter, option, index)
            return
        if hasattr(check, "value"):
            state_value = check.value
        else:
            try:
                state_value = int(check)
            except (TypeError, ValueError):
                super().paint(painter, option, index)
                return
        if state_value == Qt.CheckState.Checked.value:
            opts = QStyleOptionButton()
            opts.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_On
        elif state_value == Qt.CheckState.PartiallyChecked.value:
            opts = QStyleOptionButton()
            opts.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_NoChange
        else:
            opts = QStyleOptionButton()
            opts.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Off
        indicator_size = (
            QApplication.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, opts).size()
        )
        x = option.rect.x() + (option.rect.width() - indicator_size.width()) // 2
        y = option.rect.y() + (option.rect.height() - indicator_size.height()) // 2
        opts.rect = QRect(x, y, indicator_size.width(), indicator_size.height())
        QApplication.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_IndicatorCheckBox, opts, painter
        )

    # When True, multi-toggle is restricted to the clicked column (tree views).
    # When False, every selected cell toggles regardless of column (filter grid).
    restrict_to_column = True

    def editorEvent(self, event, model, option, index) -> bool:
        if index.data(Qt.ItemDataRole.CheckStateRole) is None:
            return super().editorEvent(event, model, option, index)
        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            current = index.data(Qt.ItemDataRole.CheckStateRole)
            current_value = current.value if hasattr(current, "value") else int(current)
            new_state = (
                Qt.CheckState.Unchecked.value
                if current_value == Qt.CheckState.Checked.value
                else Qt.CheckState.Checked.value
            )
            col = index.column()
            targets = {index}
            view = self.parent()
            if view is not None and hasattr(view, "selectionModel"):
                sel = view.selectionModel()
                if sel.isSelected(index):
                    for sel_idx in sel.selectedIndexes():
                        if self.restrict_to_column and sel_idx.column() != col:
                            continue
                        targets.add(sel_idx)
            if len(targets) > 1:
                with tool.Loin.defer_spec_membership_changed():
                    for target in targets:
                        model.setData(target, new_state, Qt.ItemDataRole.CheckStateRole)
            else:
                for target in targets:
                    model.setData(target, new_state, Qt.ItemDataRole.CheckStateRole)
            return True
        return False


class _FilterCheckDelegate(_CenteredCheckDelegate):
    """Centered-checkbox delegate that toggles every selected cell, any column."""

    restrict_to_column = False


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
        signals = tool.Loin.get_signals()
        signals.added_classes_changed.connect(self._reset_preserving_expansion)
        signals.purposes_changed.connect(self._reset_preserving_expansion)
        signals.milestones_changed.connect(self._reset_preserving_expansion)
        signals.loin_reset.connect(self._reset_view)
        signals.spec_membership_changed.connect(self._emit_check_data_changed)

    def register_view(self, view: QTreeView) -> None:
        if view not in self._tracked_views:
            self._tracked_views.append(view)
            view.setItemDelegate(_CenteredCheckDelegate(view))

    # ------------------------------------------------------------------ basics

    def _reset_view(self) -> None:
        self.beginResetModel()
        self.endResetModel()

    def _emit_check_data_changed(self) -> None:
        """Repaint check columns in-place without resetting the model."""
        nc = self.columnCount()
        if nc <= self._prefix_cols:
            return

        def walk(parent: QModelIndex) -> None:
            count = self.rowCount(parent)
            if not count:
                return
            tl = self.index(0, self._prefix_cols, parent)
            br = self.index(count - 1, nc - 1, parent)
            if tl.isValid() and br.isValid():
                self.dataChanged.emit(tl, br, [Qt.ItemDataRole.CheckStateRole])
            for row in range(count):
                walk(self.index(row, 0, parent))

        walk(QModelIndex())

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

    def rowCount(self, /, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return 0
        if not parent.isValid():
            return len(_get_root_classes())
        parent_class: BsddClass = parent.internalPointer()
        return len(_get_children(parent_class))

    def columnCount(self, _parent=QModelIndex()) -> int:
        return self._prefix_cols + len(_current_purposes()) * len(_current_milestones())

    def parent(self, index: QModelIndex) -> QModelIndex:
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
            siblings = _get_children(gp_cls) if gp_cls is not None else _get_root_classes()
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
                tool.Loin.set_class_included(payload, pm[0], pm[1], included)
            elif isinstance(payload, BsddClassProperty):
                # The property view nests properties under a pset string; the
                # underlying class is held on the source model.
                bsdd_class = self._owning_class_for_property_view(index)
                if bsdd_class is None:
                    return False
                tool.Loin.set_property_included(bsdd_class, payload, pm[0], pm[1], included)
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
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    # ------------------------------------------------------------------ state lookups

    def _check_state(self, index: QModelIndex) -> Qt.CheckState:
        pm = _column_to_guids(index.column(), self._prefix_cols)
        if pm is None:
            return Qt.CheckState.Unchecked
        payload = index.internalPointer()
        if isinstance(payload, BsddClass):
            return (
                Qt.CheckState.Checked
                if tool.Loin.is_class_included(payload, pm[0], pm[1])
                else Qt.CheckState.Unchecked
            )
        if isinstance(payload, BsddClassProperty):
            bsdd_class = self._owning_class_for_property_view(index)
            if bsdd_class is None:
                return Qt.CheckState.Unchecked
            return (
                Qt.CheckState.Checked
                if tool.Loin.is_property_included(bsdd_class, payload, pm[0], pm[1])
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

    def headerData(self, section, orientation, /, role=...):
        if orientation == Qt.Orientation.Vertical:
            return None
        if section >= self._prefix_cols:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return ["Name", "Code"][section]
        return None


# ---------------------------------------------------------------------------
# Property tree model — psets as roots, BsddClassProperty as children
# ---------------------------------------------------------------------------


class PropertyModel(QAbstractItemModel):
    """Two-level tree for the PropertyView.

    Root rows  : PropertySet names (``str``).
    Child rows : ``BsddClassProperty`` objects within that pset.
    Columns 0  : display name (property name or pset name).
    Column  1  : data type (property rows only).
    Columns ≥2 : UC×MS check states via ``tool.Loin``.
    """

    _prefix_cols: int = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bsdd_data: Optional[BsddClass] = None
        self._pset_names_cache: Optional[list[str]] = None
        self._props_for_pset_cache: dict[str, list[BsddClassProperty]] = {}
        self._tracked_views: list[QTreeView] = []

        signals = tool.Loin.get_signals()
        signals.purposes_changed.connect(self._reset_view)
        signals.milestones_changed.connect(self._reset_view)
        signals.loin_reset.connect(self._reset_view)
        signals.spec_membership_changed.connect(self._emit_check_data_changed)

    @property
    def bsdd_data(self) -> Optional[BsddClass]:
        return self._bsdd_data

    @bsdd_data.setter
    def bsdd_data(self, value: Optional[BsddClass]) -> None:
        self._bsdd_data = value
        self._invalidate_caches()

    def _invalidate_caches(self) -> None:
        self._pset_names_cache = None
        self._props_for_pset_cache = {}

    def register_view(self, view: QTreeView) -> None:
        if view not in self._tracked_views:
            self._tracked_views.append(view)
            view.setItemDelegate(_CenteredCheckDelegate(view))

    # ------------------------------------------------------------------ helpers

    def _reset_view(self) -> None:
        self._invalidate_caches()
        self.beginResetModel()
        self.endResetModel()

    def _emit_check_data_changed(self) -> None:
        """Repaint check columns in-place without resetting the model."""
        nc = self.columnCount()
        if nc <= self._prefix_cols:
            return
        psets = self._pset_names()
        if not psets:
            return
        self.dataChanged.emit(
            self.index(0, self._prefix_cols),
            self.index(len(psets) - 1, nc - 1),
            [Qt.ItemDataRole.CheckStateRole],
        )
        for row, pset_name in enumerate(psets):
            props = self._props_for_pset(pset_name)
            if not props:
                continue
            parent_idx = self.index(row, 0)
            self.dataChanged.emit(
                self.index(0, self._prefix_cols, parent_idx),
                self.index(len(props) - 1, nc - 1, parent_idx),
                [Qt.ItemDataRole.CheckStateRole],
            )

    def _collect_expanded(self, view: QTreeView) -> set[str]:
        expanded: set[str] = set()
        for row in range(self.rowCount(QModelIndex())):
            idx = self.index(row, 0)
            if idx.isValid() and view.isExpanded(idx):
                ptr = idx.internalPointer()
                if isinstance(ptr, str):
                    expanded.add(ptr)
        return expanded

    def _apply_expanded(self, view: QTreeView, expanded: set[str]) -> None:
        for row in range(self.rowCount(QModelIndex())):
            idx = self.index(row, 0)
            if idx.isValid() and idx.internalPointer() in expanded:
                view.setExpanded(idx, True)

    def _reset_preserving_expansion(self) -> None:
        self._invalidate_caches()
        snapshots = [(v, self._collect_expanded(v)) for v in self._tracked_views]
        self.beginResetModel()
        self.endResetModel()
        for view, expanded in snapshots:
            self._apply_expanded(view, expanded)

    def _pset_names(self) -> list[str]:
        if self._bsdd_data is None:
            return []
        if self._pset_names_cache is None:
            self._pset_names_cache = (
                tool.PropertySetTableView.get_pset_names_with_temporary(self._bsdd_data)
            )
        return self._pset_names_cache

    def _props_for_pset(self, pset_name: str) -> list[BsddClassProperty]:
        if self._bsdd_data is None:
            return []
        cached = self._props_for_pset_cache.get(pset_name)
        if cached is None:
            cached = prop_utils.get_class_properties_by_pset_name(self._bsdd_data, pset_name)
            self._props_for_pset_cache[pset_name] = cached
        return cached

    # ------------------------------------------------------------------ QAbstractItemModel

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid() and parent.column() != 0:
            return 0
        if not parent.isValid():
            return len(self._pset_names())
        ptr = parent.internalPointer()
        if isinstance(ptr, str):
            return len(self._props_for_pset(ptr))
        return 0

    def columnCount(self, _parent=QModelIndex()) -> int:
        return self._prefix_cols + len(_current_purposes()) * len(_current_milestones())

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()
        if not parent.isValid():
            psets = self._pset_names()
            if 0 <= row < len(psets):
                return self.createIndex(row, column, psets[row])
            return QModelIndex()
        ptr = parent.internalPointer()
        if isinstance(ptr, str):
            props = self._props_for_pset(ptr)
            if 0 <= row < len(props):
                return self.createIndex(row, column, props[row])
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        ptr = index.internalPointer()
        if isinstance(ptr, str):
            return QModelIndex()
        pset_name = getattr(ptr, "PropertySet", None)
        if pset_name is None:
            return QModelIndex()
        psets = self._pset_names()
        if pset_name in psets:
            return self.createIndex(psets.index(pset_name), 0, pset_name)
        return QModelIndex()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() >= self._prefix_cols and self.bsdd_data is not None:
            base |= Qt.ItemFlag.ItemIsUserCheckable
        return base

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        col = index.column()
        ptr = index.internalPointer()

        if role == Qt.ItemDataRole.CheckStateRole:
            if col < self._prefix_cols:
                return None
            return self._check_state(index)

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if isinstance(ptr, str):
                return ptr if col == 0 else None
            if isinstance(ptr, BsddClassProperty):
                if col == 0:
                    return prop_utils.get_name(ptr) or ptr.Code
                if col == 1:
                    return prop_utils.get_data_type(ptr)
        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:
        if role != Qt.ItemDataRole.CheckStateRole:
            return False
        col = index.column()
        if col < self._prefix_cols:
            return False
        pm = _column_to_guids(col, self._prefix_cols)
        if pm is None or self.bsdd_data is None:
            return False
        ptr = index.internalPointer()
        included = Qt.CheckState(value) == Qt.CheckState.Checked

        if isinstance(ptr, str):
            tool.Loin.set_pset_included(
                [(self.bsdd_data, self._props_for_pset(ptr))], pm[0], pm[1], included
            )
            return True
        if isinstance(ptr, BsddClassProperty):
            tool.Loin.set_property_included(self.bsdd_data, ptr, pm[0], pm[1], included)
            return True
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Vertical:
            return None
        if section >= self._prefix_cols:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return ["Name", "Data Type"][section]
        return None

    def mapToSource(self, index: QModelIndex) -> QModelIndex:
        """Pass-through so callers that assume a proxy model still work."""
        return index

    # ------------------------------------------------------------------ check state

    def _check_state(self, index: QModelIndex) -> Qt.CheckState:
        pm = _column_to_guids(index.column(), self._prefix_cols)
        if pm is None or self.bsdd_data is None:
            return Qt.CheckState.Unchecked
        ptr = index.internalPointer()

        if isinstance(ptr, BsddClassProperty):
            included = tool.Loin.is_property_included(self.bsdd_data, ptr, pm[0], pm[1])
            return Qt.CheckState.Checked if included else Qt.CheckState.Unchecked

        if isinstance(ptr, str):
            props = self._props_for_pset(ptr)
            if not props:
                return Qt.CheckState.Unchecked
            states = [
                tool.Loin.is_property_included(self.bsdd_data, p, pm[0], pm[1]) for p in props
            ]
            if all(states):
                return Qt.CheckState.Checked
            if any(states):
                return Qt.CheckState.PartiallyChecked
            return Qt.CheckState.Unchecked

        return Qt.CheckState.Unchecked


# ---------------------------------------------------------------------------
# Pset tree model — psets as roots, unique properties as children
# ---------------------------------------------------------------------------


class _PsetNode:
    """One row per unique PropertySet name across all added classes."""

    __slots__ = ("name", "entries")

    def __init__(self, name: str) -> None:
        self.name = name
        self.entries: list[_PropEntry] = []


class _PropEntry:
    """One row per unique (pset, property-code) pair; holds all class instances."""

    __slots__ = ("pset_node", "code", "name", "instances")

    def __init__(self, pset_node: _PsetNode, code: str, name: str) -> None:
        self.pset_node = pset_node
        self.code = code
        self.name = name
        self.instances: list[tuple[BsddClass, BsddClassProperty]] = []


class PsetModel(QAbstractItemModel):
    """Two-level tree: pset names as roots, unique properties as children.

    Column 0  : name (pset name or property display name).
    Column 1  : data type (property rows only).
    Columns ≥2 : UC×MS check states.

    Check state aggregates across ALL added classes that own the pset/property.
    Toggling a pset row applies to every property in every class that has it.
    Toggling a property row applies to every class that owns that property.
    """

    _prefix_cols: int = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracked_views: list[QTreeView] = []
        self._pset_cache: Optional[list[_PsetNode]] = None

        signals = tool.Loin.get_signals()
        signals.purposes_changed.connect(self._reset_view)
        signals.milestones_changed.connect(self._reset_view)
        signals.loin_reset.connect(self._reset_view)
        signals.added_classes_changed.connect(self._reset_view)
        signals.spec_membership_changed.connect(self._emit_check_data_changed)

    def register_view(self, view: QTreeView) -> None:
        if view not in self._tracked_views:
            self._tracked_views.append(view)
            view.setItemDelegate(_CenteredCheckDelegate(view))

    def mapToSource(self, index: QModelIndex) -> QModelIndex:
        return index

    # ------------------------------------------------------------------ helpers

    def _reset_view(self) -> None:
        self._pset_cache = None
        self.beginResetModel()
        self.endResetModel()

    def _get_added_classes(self) -> list[BsddClass]:
        bsdd_dict = tool.Project.get()
        if bsdd_dict is None:
            return []
        return [c for c in bsdd_dict.Classes if tool.Loin.is_class_added(c)]

    def _get_pset_cache(self) -> list[_PsetNode]:
        if self._pset_cache is not None:
            return self._pset_cache
        pset_map: dict[str, _PsetNode] = {}
        prop_map: dict[tuple[str, str], _PropEntry] = {}
        result: list[_PsetNode] = []
        for bsdd_class in self._get_added_classes():
            for cp in bsdd_class.ClassProperties:
                pset_name = cp.PropertySet or ""
                prop_code = cp.Code or ""
                if pset_name not in pset_map:
                    node = _PsetNode(pset_name)
                    pset_map[pset_name] = node
                    result.append(node)
                node = pset_map[pset_name]
                key = (pset_name, prop_code)
                if key not in prop_map:
                    entry = _PropEntry(node, prop_code, prop_utils.get_name(cp) or prop_code)
                    prop_map[key] = entry
                    node.entries.append(entry)
                prop_map[key].instances.append((bsdd_class, cp))
        self._pset_cache = result
        return result

    def _emit_check_data_changed(self) -> None:
        nodes = self._get_pset_cache()
        if not nodes:
            return
        nc = self.columnCount()
        # Root rows
        self.dataChanged.emit(
            self.index(0, self._prefix_cols),
            self.index(len(nodes) - 1, nc - 1),
            [Qt.ItemDataRole.CheckStateRole],
        )
        # Child rows — parent() uses _PropEntry.pset_node (same object → same id)
        for r, node in enumerate(nodes):
            if not node.entries:
                continue
            parent_idx = self.index(r, 0)
            self.dataChanged.emit(
                self.index(0, self._prefix_cols, parent_idx),
                self.index(len(node.entries) - 1, nc - 1, parent_idx),
                [Qt.ItemDataRole.CheckStateRole],
            )

    # ------------------------------------------------------------------ QAbstractItemModel

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid() and parent.column() != 0:
            return 0
        if not parent.isValid():
            return len(self._get_pset_cache())
        ptr = parent.internalPointer()
        if isinstance(ptr, _PsetNode):
            return len(ptr.entries)
        return 0

    def columnCount(self, _parent=QModelIndex()) -> int:
        return self._prefix_cols + len(_current_purposes()) * len(_current_milestones())

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()
        if not parent.isValid():
            nodes = self._get_pset_cache()
            if 0 <= row < len(nodes):
                return self.createIndex(row, column, nodes[row])
            return QModelIndex()
        ptr = parent.internalPointer()
        if isinstance(ptr, _PsetNode) and 0 <= row < len(ptr.entries):
            return self.createIndex(row, column, ptr.entries[row])
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        ptr = index.internalPointer()
        if isinstance(ptr, _PsetNode):
            return QModelIndex()
        if isinstance(ptr, _PropEntry):
            nodes = self._get_pset_cache()
            pset_node = ptr.pset_node
            try:
                row = nodes.index(pset_node)
            except ValueError:
                return QModelIndex()
            return self.createIndex(row, 0, pset_node)
        return QModelIndex()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() >= self._prefix_cols:
            base |= Qt.ItemFlag.ItemIsUserCheckable
        return base

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        col = index.column()
        ptr = index.internalPointer()

        if role == Qt.ItemDataRole.CheckStateRole:
            if col < self._prefix_cols:
                return None
            return self._check_state(index)

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if isinstance(ptr, _PsetNode):
                return ptr.name if col == 0 else None
            if isinstance(ptr, _PropEntry):
                if col == 0:
                    return ptr.name
                if col == 1 and ptr.instances:
                    return prop_utils.get_data_type(ptr.instances[0][1])
        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:
        if role != Qt.ItemDataRole.CheckStateRole:
            return False
        col = index.column()
        if col < self._prefix_cols:
            return False
        pm = _column_to_guids(col, self._prefix_cols)
        if pm is None:
            return False
        ptr = index.internalPointer()
        included = Qt.CheckState(value) == Qt.CheckState.Checked

        if isinstance(ptr, _PsetNode):
            pairs = [(bc, [cp]) for entry in ptr.entries for bc, cp in entry.instances]
            tool.Loin.set_pset_included(pairs, pm[0], pm[1], included)
            return True

        if isinstance(ptr, _PropEntry):
            pairs = [(bc, [cp]) for bc, cp in ptr.instances]
            tool.Loin.set_pset_included(pairs, pm[0], pm[1], included)
            return True

        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Vertical:
            return None
        if section >= self._prefix_cols:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return ["PropertySet / Property", "Data Type"][section]
        return None

    # ------------------------------------------------------------------ check state

    def _check_state(self, index: QModelIndex) -> Qt.CheckState:
        pm = _column_to_guids(index.column(), self._prefix_cols)
        if pm is None:
            return Qt.CheckState.Unchecked
        ptr = index.internalPointer()

        if isinstance(ptr, _PropEntry):
            total = len(ptr.instances)
            if not total:
                return Qt.CheckState.Unchecked
            n = sum(
                1
                for bc, cp in ptr.instances
                if tool.Loin.is_property_included(bc, cp, pm[0], pm[1])
            )
            if n == total:
                return Qt.CheckState.Checked
            return Qt.CheckState.PartiallyChecked if n else Qt.CheckState.Unchecked

        if isinstance(ptr, _PsetNode):
            total = included = 0
            for entry in ptr.entries:
                for bc, cp in entry.instances:
                    total += 1
                    if tool.Loin.is_property_included(bc, cp, pm[0], pm[1]):
                        included += 1
            if not total:
                return Qt.CheckState.Unchecked
            if included == total:
                return Qt.CheckState.Checked
            return Qt.CheckState.PartiallyChecked if included else Qt.CheckState.Unchecked

        return Qt.CheckState.Unchecked


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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_uc_ms_menu)
        self._hover_row: str | None = None  # "uc", "ms", or None
        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)

        signals = tool.Loin.get_signals()
        signals.purposes_changed.connect(self._on_loin_changed)
        signals.milestones_changed.connect(self._on_loin_changed)
        signals.loin_reset.connect(self._on_loin_changed)

    def eventFilter(self, obj, event) -> bool:
        if obj is self.viewport():
            t = event.type()
            if t == QEvent.Type.MouseMove:
                if self.logicalIndexAt(event.pos()) < 0:
                    row = "uc" if event.pos().y() < self.TOP_H else "ms"
                else:
                    row = None
                if row != self._hover_row:
                    self._hover_row = row
                    self.viewport().update()
            elif t == QEvent.Type.Leave:
                if self._hover_row is not None:
                    self._hover_row = None
                    self.viewport().update()
        return False

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            col = self.logicalIndexAt(event.pos())
            if col < 0:
                if event.pos().y() < self.TOP_H:
                    self._add_uc()
                else:
                    self._add_ms()
                return
        super().mousePressEvent(event)

    def _show_uc_ms_menu(self, pos) -> None:
        col = self.logicalIndexAt(pos)
        in_uc_row = pos.y() < self.TOP_H
        purposes = _current_purposes()
        milestones = _current_milestones()
        menu = QMenu(self)

        if col >= self._prefix_cols and purposes and milestones:
            guids = _column_to_guids(col, self._prefix_cols)
            if guids:
                p_guid, m_guid = guids
                purpose = next((p for p in purposes if p.guid == p_guid), None)
                milestone = next((m for m in milestones if m.guid == m_guid), None)

                if purpose and milestone:
                    p_name = tool.Loin.purpose_display_name(purpose)
                    m_name = tool.Loin.milestone_display_name(milestone)
                    p_idx = purposes.index(purpose)
                    m_idx = milestones.index(milestone)
                    view = self.parentWidget()

                    if in_uc_row:
                        menu.addAction(f"Rename '{p_name}'…", lambda g=p_guid: self._rename_uc(g))
                        menu.addAction(f"Remove '{p_name}'", lambda g=p_guid: self._remove_uc(g))
                        menu.addSeparator()
                        for mi, ms in enumerate(milestones):
                            ms_name = tool.Loin.milestone_display_name(ms)
                            ms_col = self._prefix_cols + p_idx * len(milestones) + mi
                            visible = view is None or not view.isColumnHidden(ms_col)
                            act = menu.addAction(f"'{ms_name}'")
                            act.setCheckable(True)
                            act.setChecked(visible)
                            act.triggered.connect(
                                lambda _=None, pg=p_guid, mg=ms.guid: (
                                    get_filter_window().toggle_combination(pg, mg)
                                )
                            )
                    else:
                        menu.addAction(f"Rename '{m_name}'…", lambda g=m_guid: self._rename_ms(g))
                        menu.addAction(f"Remove '{m_name}'", lambda g=m_guid: self._remove_ms(g))
                        menu.addSeparator()
                        for pi, pu in enumerate(purposes):
                            pu_name = tool.Loin.purpose_display_name(pu)
                            pu_col = self._prefix_cols + pi * len(milestones) + m_idx
                            visible = view is None or not view.isColumnHidden(pu_col)
                            act = menu.addAction(f"'{pu_name}'")
                            act.setCheckable(True)
                            act.setChecked(visible)
                            act.triggered.connect(
                                lambda _=None, pg=pu.guid, mg=m_guid: (
                                    get_filter_window().toggle_combination(pg, mg)
                                )
                            )

                    menu.addSeparator()

        menu.addAction("Add Use Case…", self._add_uc)
        menu.addAction("Add Milestone…", self._add_ms)
        menu.addSeparator()
        menu.addAction("Edit Use Cases / Milestones", self._open_filter_window)
        menu.exec(self.viewport().mapToGlobal(pos))

    def _open_filter_window(self) -> None:
        win = get_filter_window()
        win.show()
        win.raise_()
        win.activateWindow()

    def _ask_name(self, prompt: str) -> str | None:
        name, ok = QInputDialog.getText(self, "Name", prompt)
        return name.strip() if ok and name.strip() else None

    def _add_uc(self) -> None:
        name = self._ask_name("Use case name:")
        if name:
            tool.Loin.add_purpose(name)

    def _add_ms(self) -> None:
        name = self._ask_name("Milestone name:")
        if name:
            tool.Loin.add_milestone(name)

    def _rename_uc(self, guid: UUID) -> None:
        new = self._ask_name("Use case name:")
        if new:
            tool.Loin.rename_purpose(guid, new)

    def _rename_ms(self, guid: UUID) -> None:
        new = self._ask_name("Milestone name:")
        if new:
            tool.Loin.rename_milestone(guid, new)

    def _remove_uc(self, guid: UUID) -> None:
        tool.Loin.remove_purpose(guid)

    def _remove_ms(self, guid: UUID) -> None:
        tool.Loin.remove_milestone(guid)

    def _on_loin_changed(self) -> None:
        self.updateGeometry()
        self.viewport().update()

    def _bot_height(self) -> int:
        fm = self.fontMetrics()
        milestones = _current_milestones()
        if not milestones:
            return self._PADDING
        return (
            max(fm.horizontalAdvance(tool.Loin.milestone_display_name(m)) for m in milestones)
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
                label = (
                    self.model().headerData(
                        col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
                    )
                    or ""
                )
            self._draw_cell(painter, x, 0, w, total_h, str(label), bold)
            x += w

        purposes = _current_purposes()
        milestones = _current_milestones()
        num_ms = len(milestones)
        for ui_idx, purpose in enumerate(purposes):
            first_col = self._prefix_cols + ui_idx * num_ms
            x_uc = sum(self.sectionSize(c) for c in range(first_col)) - self.offset()
            w_uc = sum(self.sectionSize(first_col + m) for m in range(num_ms))
            uc_name = tool.Loin.purpose_display_name(purpose)
            self._draw_cell(painter, x_uc, 0, w_uc, self.TOP_H, uc_name, bold)

            x_ms = x_uc
            for mi, milestone in enumerate(milestones):
                w_ms = self.sectionSize(first_col + mi)
                ms_name = tool.Loin.milestone_display_name(milestone)
                self._draw_cell(painter, x_ms, self.TOP_H, w_ms, bot_h, ms_name, rotated=True)
                x_ms += w_ms

        # Hover hint in the empty space beyond the last section
        if self._hover_row is not None:
            total_cols = self._prefix_cols + len(purposes) * len(milestones)
            hint_x = sum(self.sectionSize(c) for c in range(total_cols)) - self.offset()
            hint_w = self.viewport().width() - hint_x
            if hint_w > 20:
                highlight = self.palette().highlight().color()
                bg = self.palette().highlight().color()
                bg.setAlpha(30)
                if self._hover_row == "uc":
                    rect = QRect(hint_x, 0, hint_w, self.TOP_H)
                    label = "+ New UC"
                else:
                    rect = QRect(hint_x, self.TOP_H, hint_w, bot_h)
                    label = "+ New MS"
                painter.fillRect(rect, bg)
                painter.setPen(highlight)
                painter.drawRect(rect.adjusted(0, 0, -1, -1))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

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

        signals = tool.Loin.get_signals()
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

    def checked_combinations(self) -> set[tuple[UUID, UUID]]:
        """Return (purpose_guid, milestone_guid) pairs checked in the filter table."""
        purposes = _current_purposes()
        milestones = _current_milestones()
        result: set[tuple[UUID, UUID]] = set()
        if self._filter_table is None:
            return result
        for p_idx, purpose in enumerate(purposes):
            for m_idx, milestone in enumerate(milestones):
                item = self._filter_table.item(p_idx, m_idx)
                if item is not None and item.checkState() == Qt.CheckState.Checked:
                    result.add((purpose.guid, milestone.guid))
        return result

    def toggle_combination(self, purpose_guid: UUID, milestone_guid: UUID) -> None:
        """Toggle visibility of the given purpose × milestone column on all views."""
        purposes = _current_purposes()
        milestones = _current_milestones()
        p_idx = next((i for i, p in enumerate(purposes) if p.guid == purpose_guid), None)
        m_idx = next((i for i, m in enumerate(milestones) if m.guid == milestone_guid), None)
        if p_idx is None or m_idx is None or self._filter_table is None:
            return
        item = self._filter_table.item(p_idx, m_idx)
        if item is None:
            return
        new_state = (
            Qt.CheckState.Unchecked
            if item.checkState() == Qt.CheckState.Checked
            else Qt.CheckState.Checked
        )
        item.setCheckState(new_state)
        # _on_filter_changed fires via itemChanged and updates all views

    # ------------------------------------------------------------------ table

    def _build_table(self) -> QTableWidget:
        purposes = _current_purposes()
        milestones = _current_milestones()
        table = QTableWidget(len(purposes), len(milestones))
        table.setVerticalHeaderLabels([tool.Loin.purpose_display_name(p) for p in purposes])
        table.setHorizontalHeaderLabels([tool.Loin.milestone_display_name(m) for m in milestones])
        table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        table.setItemDelegate(_FilterCheckDelegate(table))
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

        existing_specs = tool.Loin.get_properties().specs
        for ui_idx, purpose in enumerate(purposes):
            for mi, milestone in enumerate(milestones):
                item = QTableWidgetItem()
                item.setFlags(
                    Qt.ItemFlag.ItemIsUserCheckable
                    | Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsSelectable
                )
                has_spec = (purpose.guid, milestone.guid) in existing_specs
                item.setCheckState(
                    Qt.CheckState.Checked if has_spec else Qt.CheckState.Unchecked
                )
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
        vh.setSectionsMovable(True)
        vh.sectionMoved.connect(self._on_purpose_moved)

        hh = table.horizontalHeader()
        hh.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        hh.customContextMenuRequested.connect(self._ms_context_menu)
        hh.setSectionsMovable(True)
        hh.sectionMoved.connect(self._on_milestone_moved)

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

    def _on_purpose_moved(self, *_args) -> None:
        """Translate a row-header drag into a Loin.reorder_purposes call.

        After the tool fires purposes_changed, _rebuild_table redraws from
        scratch so the header's visual order resets to logical — no manual
        moveSection cleanup needed here.
        """
        if self._filter_table is None:
            return
        purposes = _current_purposes()
        if not purposes:
            return
        vh = self._filter_table.verticalHeader()
        new_order = [purposes[vh.logicalIndex(v)].guid for v in range(len(purposes))]
        tool.Loin.reorder_purposes(new_order)

    def _on_milestone_moved(self, *_args) -> None:
        if self._filter_table is None:
            return
        milestones = _current_milestones()
        if not milestones:
            return
        hh = self._filter_table.horizontalHeader()
        new_order = [milestones[hh.logicalIndex(v)].guid for v in range(len(milestones))]
        tool.Loin.reorder_milestones(new_order)

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
            label = tool.Loin.purpose_display_name(purposes[idx])
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
            label = tool.Loin.milestone_display_name(milestones[idx])
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
            tool.Loin.add_purpose(name)

    def _add_ms(self) -> None:
        name = self._ask_name("Milestone name:")
        if name:
            tool.Loin.add_milestone(name)

    def _remove_uc(self, guid: UUID) -> None:
        tool.Loin.remove_purpose(guid)

    def _remove_ms(self, guid: UUID) -> None:
        tool.Loin.remove_milestone(guid)

    def _rename_uc(self, guid: UUID) -> None:
        new = self._ask_name("Use case name:")
        if new:
            tool.Loin.rename_purpose(guid, new)

    def _rename_ms(self, guid: UUID) -> None:
        new = self._ask_name("Milestone name:")
        if new:
            tool.Loin.rename_milestone(guid, new)

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
        prov = tool.Loin.get_providing_actor()
        recv = tool.Loin.get_receiving_actor()
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
            tool.Loin.set_providing_actor(
                role=prov_role,
                affiliation=self._le_prov_aff.text().strip() or None,
                email_address=self._le_prov_email.text().strip() or None,
            )
        if recv_role:
            tool.Loin.set_receiving_actor(
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
