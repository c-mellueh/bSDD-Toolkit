from __future__ import annotations
from typing import Iterable, Optional

from PySide6.QtCore import (
    QPoint,
    QRect,
    QSize,
    Qt,
    Signal,
    QRect,
    QSize,
    QPoint,
    Qt,
    QEvent,
    QTimer,
)
from PySide6.QtGui import QFontMetrics, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFrame,
    QLabel,
    QToolButton,
    QStyle,
    QStyleOption,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
    QLayout,
    QLayoutItem,
    QCompleter,
    QLayout,
    QLayoutItem,
    QWidgetItem,
    QSizePolicy,
    QStylePainter,
)
import logging

STYLE_SHEET = """
        #Chip {
            border: 1px solid palette(mid);
            border-radius: 10px;
            background: palette(base);
        }
        #ChipLabel { padding: 0px; }
        #ChipClose { padding: 0px; }
        """
STYLE_SHEET2 = """
    QLineEdit {
        border: 1px solid palette(mid);
        border-radius: 10px;
        background: palette(base);
        padding: 2px 6px;
    }
    """


# ---------------------------
# FlowLayout (wraps children)
# ---------------------------
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=6, hspacing=6, vspacing=6):
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._hspace = hspacing
        self._vspace = vspacing
        self.setContentsMargins(margin, margin, margin, margin)

    # ---- Qt API ----
    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)

    def addWidget(self, w) -> None:
        super().addWidget(w)  # creates QWidgetItem and calls addItem

    def insertWidget(self, index: int, w) -> None:
        self.addChildWidget(w)
        self._items.insert(index, QWidgetItem(w))
        self.invalidate()  # <— trigger relayout

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index: int):
        item = self._items.pop(index) if 0 <= index < len(self._items) else None
        if item:
            self.invalidate()  # <— trigger relayout
        return item

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    # ---- layouting ----
    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        m = self.contentsMargins()
        effective = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x = effective.x()
        y = effective.y()
        line_h = 0

        for item in self._items:
            hint = item.sizeHint()
            iw, ih = hint.width(), hint.height()

            if x + iw > effective.right() + 1 and line_h > 0:
                x = effective.x()
                y += line_h + self._vspace
                line_h = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))

            x += iw + self._hspace
            line_h = max(line_h, ih)

        # total height used (including margins)
        return y + line_h - rect.y() + m.top() + m.bottom()

    def invalidate(self) -> None:
        super().invalidate()
        # Ask parent to recalc sizes and repaint
        pw = self.parentWidget()
        if pw:
            pw.updateGeometry()
            pw.update()


# Chip widget
# ---------------------------
class Chip(QFrame):
    removed = Signal(str)

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._text = text
        self.setObjectName("Chip")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        self._label = QLabel(text)
        self._label.setObjectName("ChipLabel")
        self._label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._close = QToolButton()
        self._close.setObjectName("ChipClose")
        self._close.setAutoRaise(True)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.setText("×")
        self._close.clicked.connect(lambda: self.removed.emit(self._text))

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 2, 4, 2)
        lay.setSpacing(4)
        lay.addWidget(self._label)
        lay.addWidget(self._close)

        # Simple styling (override with your QSS if you want)
        self.setStyleSheet(STYLE_SHEET)

    def text(self) -> str:
        return self._text

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        m = self.layout().contentsMargins()
        w = (
            fm.horizontalAdvance(self._text)
            + m.left()
            + m.right()
            + self.layout().spacing()
            + self._close.sizeHint().width()
        )
        h = max(24, fm.height() + m.top() + m.bottom())
        return QSize(w, h)


# ---------------------------
# TagInput widget
# ---------------------------


class TagInput(QWidget):
    tagsChanged = Signal(list)

    def __init__(
        self,
        parent=None,
        placeholder: str = "Add tag…",
        allowed: list[str] | None = None,
        minimum_le_width: int = 250,
    ):
        super().__init__(parent)
        self._tags: list[str] = []
        self._allowed: set[str] | None = set(allowed) if allowed else None

        self._flow = FlowLayout(self, margin=6, hspacing=6, vspacing=6)

        self._edit = QLineEdit()
        self._edit.setObjectName("LineEdit")
        self._edit.setPlaceholderText(placeholder)
        self._edit.setFrame(False)
        self._edit.setMinimumWidth(minimum_le_width)
        self._edit.returnPressed.connect(self._commit_from_edit)
        self._edit.textEdited.connect(self._maybe_split_text)
        self._edit.setStyleSheet(STYLE_SHEET2)

        left, top, right, bottom = 8, 2, 4, 2
        self._edit.setTextMargins(left, top, right, bottom)
        fm = QFontMetrics(self._edit.font())
        target_h = (
            max(24, fm.height() + top + bottom) + 4
        )  # I don't know why but i need th +4 else the line edit is not high enough #TODO
        self._edit.setFixedHeight(target_h)

        if allowed:
            self._completer = QCompleter(sorted(allowed), self)
            self._completer.setCaseSensitivity(Qt.CaseInsensitive)
            self._edit.setCompleter(self._completer)

        self._completer.activated[str].connect(
            lambda text: QTimer.singleShot(0, lambda: self._complete_and_commit(text))
        )
        # make line edit part of flow
        self._proxy = QWidget()
        pl = QHBoxLayout(self._proxy)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.addWidget(self._edit)
        self._proxy.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._flow.addWidget(self._proxy)

    def _complete_and_commit(self, text: str) -> None:
        self._edit.setText(text)
        self._commit_from_edit()

    def eventFilter(self, obj, ev):
        if obj is self._edit and ev.type() == QEvent.KeyPress:
            if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
                # If the completer popup is visible, let it finalize selection,
                # then commit and clear *after* the popup writes into the line edit.
                if getattr(self, "_completer", None):
                    popup = self._completer.popup()
                    if popup and popup.isVisible():
                        QTimer.singleShot(0, self._commit_from_edit)
                        return True  # consume
        return super().eventFilter(obj, ev)

    # Public API
    def tags(self) -> list[str]:
        return list(self._tags)

    def setTags(self, tags: Iterable[str]) -> None:
        for t in list(self._tags):
            self._remove_tag(t, emit_signal=False)
        for t in tags:
            self._add_tag(str(t), emit_signal=False)
        self.tagsChanged.emit(self.tags())

    def clear(self) -> None:
        self.setTags([])

    # Internal helpers
    def _normalize(self, text: str) -> Optional[str]:
        t = text.strip()
        if not t:
            return None
        return t

    def _add_tag(self, text: str, emit_signal: bool = True) -> None:
        val = self._normalize(text)
        if val is None or val in self._tags:
            return
        if self._allowed and val not in self._allowed:
            # reject not-allowed values
            self._edit.setText("")  # clear invalid input
            return
        chip = Chip(val)
        chip.removed.connect(self._remove_tag)
        idx = self._flow.count() - 1
        self._flow.insertWidget(idx, chip)
        self._tags.append(val)
        if emit_signal:
            self.tagsChanged.emit(self.tags())

    def _remove_tag(self, text: str, emit_signal: bool = True) -> None:
        if text not in self._tags:
            return
        for i in range(self._flow.count()):
            item = self._flow.itemAt(i)
            w = item.widget() if item else None
            if isinstance(w, Chip) and w.text() == text:
                it = self._flow.takeAt(i)
                if it:
                    it.widget().deleteLater()
                break
        self._tags.remove(text)
        self._flow.invalidate()  # <— force relayout now
        if emit_signal:
            self.tagsChanged.emit(self.tags())

    def _commit_from_edit(self) -> None:
        txt = self._edit.text()
        self._edit.clear()
        self._add_tag(txt)

    def _maybe_split_text(self, text: str) -> None:
        # When user pastes a list, split on common separators and add progressively.
        separators = [",", ";", "\n", "\t"]
        if any(s in text for s in separators):
            parts = text.replace("\n", ",").replace("\t", ",").replace(";", ",").split(",")
            # Keep the last partial in the edit; commit the rest
            *finished, last = parts if parts else ([], "")
            for p in finished:
                self._add_tag(p)
            self._edit.setText(last)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if getattr(self, "_completer", None) and self._completer.popup().isVisible():
            if e.key() in (Qt.Key_Return, Qt.Key_Enter):
                # commit the currently highlighted completion
                txt = self._completer.currentCompletion() or self._edit.text()
                self._complete_and_commit(txt)
                e.accept()
                return
        # Backspace/Delete: remove last chip if caret at start
        if e.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            if (
                self._edit.hasFocus()
                and self._edit.cursorPosition() == 0
                and not self._edit.selectedText()
            ):
                if self._tags:
                    self._remove_tag(self._tags[-1])
                    return
        # Comma/space quick-commit
        if e.text() in [",", " "] and self._edit.hasFocus():
            self._commit_from_edit()
            return
        super().keyPressEvent(e)

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        h = max(32, fm.height() + 14)
        return QSize(300, h)

    # Ensure frame + style draw nicely
    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QStylePainter(self)
        p.drawPrimitive(QStyle.PE_Widget, opt)


# QStylePainter import (placed after class to avoid circular import warnings in some linters)
