from bsdd_gui.plugins.modelcheck.module.window import ui, prop
from bsdd_gui.presets.tool_presets import WidgetTool, ActionTool


class Window(WidgetTool, ActionTool):
    _properties = prop.WindowProperties()

    @classmethod
    def get_properties(cls) -> prop.WindowProperties:
        return cls._properties

    @classmethod
    def get_window(cls):
        if cls.get_properties().window is None:
            cls.get_properties().window = ui.ModelcheckWindow()
        return cls.get_properties().window

    @classmethod
    def set_action(cls, name: str, action):
        cls.get_properties().actions[name] = action

    @classmethod
    def get_action(cls, name: str):
        return cls.get_properties().actions.get(name)

    @classmethod
    def populate_class_tree(cls, dictionary):
        window = cls.get_window()
        window.class_tree.clear()
        if not dictionary or not getattr(dictionary, 'Classes', None):
            return
        from PySide6.QtWidgets import QTreeWidgetItem
        from PySide6.QtCore import Qt

        for b_class in dictionary.Classes:
            class_item = QTreeWidgetItem([
                f"{b_class.Name} ({b_class.Code})",
                "",
                getattr(b_class, 'ClassType', 'Class') or 'Class',
            ])
            class_item.setCheckState(0, Qt.CheckState.Checked)
            class_item.setData(0, Qt.ItemDataRole.UserRole, b_class)

            for cp in (b_class.ClassProperties or []):
                prop_item = QTreeWidgetItem([
                    cp.PropertyCode,
                    cp.PropertySet or "",
                    getattr(cp, 'DataType', '') or "",
                ])
                prop_item.setCheckState(0, Qt.CheckState.Checked)
                prop_item.setData(0, Qt.ItemDataRole.UserRole, cp)
                class_item.addChild(prop_item)

            window.class_tree.addTopLevelItem(class_item)
        window.class_tree.expandAll()
