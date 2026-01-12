from typing import Literal

PATH_NAME = "graph_viewer"
FILETYPE = "JSON Files (*.json);;all (*.*)"

OVERLAY_STYLESHEET = """
                QLabel {
                    color: #e8e8f0;
                    background: rgba(25, 25, 35, 180);
                    border: 1px solid rgba(80, 90, 120, 160);
                    border-radius: 8px;
                    padding: 10px 14px;
                }
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
