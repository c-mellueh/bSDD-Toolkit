from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.relationship_editor import ui


def connect_widget(
    widget: ui.RelationshipWidget, relationship_editor: Type[tool.RelationshipEditor]
):
    pass
