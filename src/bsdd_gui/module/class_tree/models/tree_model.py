# src/bsdd_gui/models/tree_model.py
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt

class Node:
    def __init__(self, obj, parent=None, kind="dict"):
        self.obj = obj
        self.parent = parent
        self.kind = kind
        self.children = []

    def child(self, row): return self.children[row]
    def row(self): return 0 if self.parent is None else self.parent.children.index(self)
    def child_count(self): return len(self.children)

class BsddTreeModel(QAbstractItemModel):
    COLS = ["Name", "Code", "Type"]  # adjust to your data

    def __init__(self, dictionary, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.root = Node(dictionary, None, "dict")
        self._build_tree()

    # --- required model methods ---
    def columnCount(self, parent): return len(self.COLS)

    def rowCount(self, parent):
        node = self.node_from_index(parent)
        return node.child_count()

    def index(self, row, col, parent):
        parent_node = self.node_from_index(parent)
        if 0 <= row < parent_node.child_count() and 0 <= col < len(self.COLS):
            return self.createIndex(row, col, parent_node.child(row))
        return QModelIndex()

    def parent(self, index):
        if not index.isValid(): return QModelIndex()
        node = self.node_from_index(index)
        if node.parent is None: return QModelIndex()
        return self.createIndex(node.parent.row(), 0, node.parent)

    def data(self, index, role):
        if not index.isValid(): return None
        node = self.node_from_index(index)
        if role in (Qt.DisplayRole, Qt.EditRole):
            col = index.column()
            if col == 0:
                return getattr(node.obj, "name", getattr(node.obj, "Name", None))
            if col == 1:
                return getattr(node.obj, "code", getattr(node.obj, "Code", None))
            if col == 2:
                return node.kind
        return None

    def setData(self, index, value, role):
        if role != Qt.EditRole or not index.isValid():
            return False
        node = self.node_from_index(index)
        col = index.column()
        if col == 0:
            ok = self.controller.rename(node.obj, value)  # delegate to parser-side edit API
        elif col == 1:
            ok = self.controller.set_code(node.obj, value)
        else:
            ok = False
        if ok:
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return ok

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        base = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() in (0, 1):  # name/code editable
            base |= Qt.ItemIsEditable
        return base

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.COLS[section]
        return None

    # --- helpers ---
    def node_from_index(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def _build_tree(self):
        """Translate your domain objects into Node tree."""
        self.beginResetModel()
        self.root.children.clear()

        d = self.root.obj
        # Adjust to your actual API:
        for cls in getattr(d, "Classes", getattr(d, "classes", [])):
            cnode = Node(cls, self.root, "class")
            self.root.children.append(cnode)

            # nested classes (if you have a hierarchy)
            for sub in getattr(cls, "Children", getattr(cls, "children", [])):
                snode = Node(sub, cnode, "class")
                cnode.children.append(snode)

            # properties
            for prop in getattr(cls, "Properties", getattr(cls, "properties", [])):
                pnode = Node(prop, cnode, "property")
                cnode.children.append(pnode)

        self.endResetModel()

    # Optional: insertion/removal wired to controller operations
    def insertRow(self, row, parent):
        parent_node = self.node_from_index(parent)
        created = self.controller.add_child(parent_node.obj)  # returns domain object
        if not created: return False
        self.beginInsertRows(parent, row, row)
        parent_node.children.insert(row, Node(created, parent_node, "class"))
        self.endInsertRows()
        return True
