
from typing import Literal

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