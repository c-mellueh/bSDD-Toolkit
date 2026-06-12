from PySide6.QtWidgets import QLineEdit, QToolButton, QStyle
from PySide6.QtCore import Qt


class LineEditWithButton(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.button = QToolButton(self)
        self.button.setText("Add Item")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setAutoRaise(True)
        self.button_mode = "new"  # if needed the button can have multiple modes like
        # palette() references resolve at draw time, so the button follows theme changes
        self.button.setStyleSheet("""
            QToolButton {
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 0px 6px;
                background-color: transparent;
            }
            QToolButton:hover { background-color: palette(midlight); }
            QToolButton:pressed { background-color: palette(mid); }
        """)

        self._update_margins_and_geometry()

    def _update_margins_and_geometry(self):
        frame_w = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        btn_size = self.button.sizeHint()

        # shrink button height relative to line edit
        target_h = int(self.height() * 0.7)
        self.button.setFixedHeight(target_h)

        # recalc width (based on text size)
        self.button.setFixedWidth(btn_size.width())

        # padding for text inside line edit
        right_padding = self.button.width() + frame_w + 4
        self.setTextMargins(0, 0, right_padding, 0)

        # position button inside, vertically centered
        x = self.rect().right() - frame_w - self.button.width()
        y = (self.rect().height() - self.button.height()) // 2
        self.button.move(x, y)

    def show_button(self, show: bool):
        self.button.setVisible(show)

    def set_button_text(self, text):
        self.button.setText(text)

    def set_button_mode(self, mode: str):
        self.button_mode = mode

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_margins_and_geometry()
