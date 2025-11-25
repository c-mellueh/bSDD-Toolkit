from typing import Iterable, Optional, Callable, Any

from PySide6.QtCore import QObject, Signal, QThread, Slot,QCoreApplication
from PySide6.QtWidgets import (
    QWidget,
    QProgressDialog,
    QProgressBar,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt


class IterableWorker(QObject):
    progress = Signal(int)
    finished = Signal()
    canceled = Signal()
    item_processed = Signal(object, int)

    def __init__(
        self,
        iterable: Iterable[Any],
        total: Optional[int] = None,
        process_func: Optional[Callable[[Any, int], None]] = None,
    ):
        super().__init__()
        self._iterable = iterable
        self._total = total
        self._process_func = process_func
        self._running = True

    @Slot()
    def run(self):
        total = self._total
        if total is None:
            try:
                total = len(self._iterable)
            except TypeError:
                total = None

        if total is None:
            current = 0
            for idx, item in enumerate(self._iterable):
                if not self._running:
                    self.canceled.emit()
                    return

                if self._process_func is not None:
                    self._process_func(item, idx)

                self.item_processed.emit(item, idx)
                current += 1
                self.progress.emit(current)

            self.finished.emit()
        else:
            for idx, item in enumerate(self._iterable):
                if not self._running:
                    self.canceled.emit()
                    return

                if self._process_func is not None:
                    self._process_func(item, idx)

                self.item_processed.emit(item, idx)
                self.progress.emit(idx + 1)

            self.finished.emit()

    @Slot()
    def stop(self):
        self._running = False


class InlineProgressWidget(QWidget):
    """
    Lightweight inline progress with a label and cancel button to embed in layouts.
    """

    canceled = Signal()

    def __init__(self, parent: QWidget, title: str, text: str, cancel_text: str, maximum: int):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._label = QLabel(f"{title} {text}".strip(), self)
        self._progress_bar = QProgressBar(self)
        self._progress_bar.setRange(0, maximum)
        self._progress_bar.setValue(0)
        self._cancel_button = QPushButton(cancel_text, self)

        self._layout.addWidget(self._label)
        self._layout.addWidget(self._progress_bar, 1)
        self._layout.addWidget(self._cancel_button)
            
        self._cancel_button.clicked.connect(self.canceled.emit)
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sp)
        self._cancel_button.hide()
        
    def setValue(self, value: int):
        self._progress_bar.setValue(value)

    def setRange(self, minimum: int, maximum: int):
        self._progress_bar.setRange(minimum, maximum)

    def close(self):
        # hide instead of destroying immediately; caller may deleteLater()
        self.hide()

def run_iterable_with_progress(
    parent: QWidget,
    iterable: Iterable[Any],
    total: Optional[int] = None,
    *,
    title: str = "Processing…",
    text: str = "Please wait…",
    cancel_text: str = "Cancel",
    process_func: Optional[Callable[[Any, int], None]] = None,
    inline_parent: Optional[QWidget] = None,
):
    """
    [Unverified] Runs an iterable in a QThread and shows a QProgressDialog or inline widget.

    Returns:
        (worker, thread, dialog)
    """
    thread = QThread()  # no parent; stays in main thread
    worker = IterableWorker(iterable, total=total, process_func=process_func)
    worker.moveToThread(thread)

    # determine total for dialog
    if total is None:
        try:
            total = len(iterable)
        except TypeError:
            total = 0

    if inline_parent is not None:
        dialog = InlineProgressWidget(inline_parent, title, text, cancel_text, max(total, 0))
        layout = inline_parent.layout()
        if isinstance(layout, QGridLayout):
            layout.addWidget(dialog, layout.rowCount(), 0, 1, max(1, layout.columnCount()))
        elif layout is not None:
            layout.addWidget(dialog)
        dialog.show()
    else:
        dialog = QProgressDialog(text, cancel_text, 0, max(total, 0), parent)
        dialog.setWindowTitle(title)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setAutoClose(True)
        dialog.setAutoReset(True)
        dialog.setMinimumDuration(0)  # show immediately
        dialog.show()
        QCoreApplication.processEvents()
    if total == 0:
        dialog.setRange(0, 0)  # busy indicator

    thread.started.connect(worker.run)
    worker.progress.connect(dialog.setValue)
    worker.finished.connect(dialog.close)
    worker.canceled.connect(dialog.close)

    dialog.canceled.connect(worker.stop)

    worker.finished.connect(thread.quit)
    worker.canceled.connect(thread.quit)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(dialog.deleteLater)

    thread.start()

    return worker, thread, dialog
