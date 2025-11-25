from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
from bsdd_gui.resources.icons import get_icon

class _Spinner(QWidget):
    """
    Simple animated arc that continuously spins to indicate background work.
    """

    def __init__(self, parent: Optional[QWidget] = None, diameter: int = 42, line_width: int = 4):
        super().__init__(parent)
        self._angle = 0
        self._line_width = line_width
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(80)  # ~12 FPS is enough for a subtle spinner

        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(size_policy)
        self.setMinimumSize(diameter, diameter)

    @Slot()
    def _advance(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, _event):  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        color = self.palette().highlight().color()
        pen = QPen(QColor(color))
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        margin = self._line_width
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        start_angle = self._angle * 16  # Qt uses 1/16 deg units
        span_angle = 240 * 16
        painter.drawArc(rect, start_angle, span_angle)


class WaitingWidget(QWidget):
    """
    Small inline widget with a spinning circle and text labels.
    """

    def __init__(self, parent: Optional[QWidget] = None, title: str = "Title", text: str = "Text"):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self._title_label = QLabel(title, self)
        self._title_label.setObjectName("waitingTitle")
        self._title_label.setStyleSheet("font-weight: 600;")

        self._text_label = QLabel(text, self)
        self._text_label.setWordWrap(True)
        self._spinner = _Spinner(self)
        self._spinner.setObjectName("waitingSpinner")

        layout.addWidget(self._title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._text_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Minimum)
        sp.setVerticalPolicy(QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sp)
        self.setWindowIcon(get_icon())
        self.setWindowTitle(title)
        if not text:
            self._text_label.hide()

    def set_title(self, title: str):
        self._title_label.setText(title)

    def set_text(self, text: str):
        self._text_label.setText(text)


class WaitingWorker(QObject):
    """
    Worker that only owns lifecycle signals. Call stop() to finish/close externally.
    """

    finished = Signal()

    @Slot()
    def run(self):
        # Nothing to do; thread event loop keeps running until stop() is called.
        return

    @Slot()
    def stop(self):
        self.finished.emit()


def start_waiting_widget(parent: QWidget, title: str = "Title", text: str = "Text"):
    """
    Create and show a WaitingWidget and return (worker, thread, widget).
    Caller should invoke worker.stop() when the main-thread task is done.
    """
    thread = QThread(parent)
    worker = WaitingWorker()
    worker.moveToThread(thread)

    waiting_widget = WaitingWidget(parent, title=title, text=text)
    waiting_widget.show()

    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(waiting_widget.close)

    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(waiting_widget.close)
    thread.finished.connect(waiting_widget.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()
    return worker, thread, waiting_widget


def stop_waiting_widget(worker: WaitingWorker):
    """
    Convenience to terminate the waiting widget created via start_waiting_widget.
    """
    worker.stop()
