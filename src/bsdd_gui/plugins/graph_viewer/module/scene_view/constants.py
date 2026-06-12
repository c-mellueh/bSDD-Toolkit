from typing import Literal

from bsdd_gui.tool.theme import rgba

PATH_NAME = "graph_viewer"
FILETYPE = "JSON Files (*.json);;all (*.*)"


def get_overlay_style_sheet(tokens: dict[str, str]) -> str:
    return f"""
                QLabel {{
                    color: {tokens["text"]};
                    background: {rgba(tokens["surface"], 200)};
                    border: 1px solid {rgba(tokens["border_strong"], 160)};
                    border-radius: 8px;
                    padding: 10px 14px;
                }}
                """


ALLOWED_DRAG_TYPES = Literal["property_drag", "class_drag"]

PROPERTY_DRAG = "property_drag"
CLASS_DRAG = "class_drag"

# Scene sizing
# Extra padding added around the bounding box of current nodes when
# computing the scene rect, to allow panning into empty space.
SCENE_PADDING = 800  # pixels
# Minimum scene size to guarantee ample panning room even for tiny graphs.
SCENE_MIN_SIZE = 100_000  # width and height in pixels
