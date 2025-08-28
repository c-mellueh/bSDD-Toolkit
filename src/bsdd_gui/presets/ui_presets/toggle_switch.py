from __future__ import annotations
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPalette
from PySide6.QtWidgets import QApplication, QAbstractButton, QWidget, QHBoxLayout, QLabel


class ToggleSwitch(QAbstractButton):
    """
    Animierter Toggle-Schalter.
    - click/space toggelt
    - toggled(bool) kommt von QAbstractButton
    - Farben via setOnColor/OffColor/HandleColor änderbar
    """

    def __init__(self, parent=None, checked: bool = False, duration_ms: int = 180):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)

        self._handle_pos: float = 1.0 if checked else 0.0
        self._hover: float = 0.0
        self._onColor: QColor | None = None
        self._offColor: QColor | None = None
        self._handleColor: QColor | None = None

        self._anim = QPropertyAnimation(self, b"handlePos", self)
        self._anim.setDuration(duration_ms)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        # Barrierefreiheit
        self.setAccessibleName("Schalter")
        self._update_accessible_description()

        # Sync Animation bei Programm-Änderungen
        self.toggled.connect(self._sync_anim_with_state)
        self.setMaximumWidth(50)

    # ----- API -----
    def setAnimationDuration(self, ms: int) -> None:
        self._anim.setDuration(int(ms))

    def setOnColor(self, color: QColor) -> None:
        self._onColor = QColor(color)
        self.update()

    def setOffColor(self, color: QColor) -> None:
        self._offColor = QColor(color)
        self.update()

    def setHandleColor(self, color: QColor) -> None:
        self._handleColor = QColor(color)
        self.update()

    # ----- QAbstractButton Hooks -----
    def nextCheckState(self) -> None:
        # Standard-Toggle + Animation
        self.setChecked(not self.isChecked())

    def _sync_anim_with_state(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._handle_pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()
        self._update_accessible_description()

    # ----- Sizing -----
    def sizeHint(self) -> QSize:
        # dynamisch an Schriftgröße, min. 22px hoch
        h = max(22, int(self.fontMetrics().height() * 1.2))
        w = int(h * 1.9)  # klassisches Seitenverhältnis
        return QSize(w, h)

    # ----- Painting -----
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect()
        r = rect.height() / 2.0

        track_rect = QRectF(rect)
        track_rect.setHeight(r * 2)
        track_rect.setY((rect.height() - track_rect.height()) / 2)
        track_rect.setX(track_rect.x() + 1)
        track_rect.setWidth(rect.width() - 2)

        onC, offC, handleC, disTrackC, disHandleC = self._colors()

        # Track-Farbe (Lerp)
        if self.isEnabled():
            t = self._handle_pos
            track_color = QColor(
                offC.red() + (onC.red() - offC.red()) * t,
                offC.green() + (onC.green() - offC.green()) * t,
                offC.blue() + (onC.blue() - offC.blue()) * t,
            )
            if self._hover:
                track_color = track_color.lighter(100 + int(self._hover * 20))
        else:
            track_color = disTrackC

        # Track
        p.setPen(Qt.NoPen)
        p.setBrush(track_color)
        p.drawRoundedRect(track_rect, r, r)

        # Handle
        margin = max(2.0, track_rect.height() * 0.09 + 1.0)
        d = track_rect.height() - 2 * margin
        travel = track_rect.width() - 2 * margin - d

        if self.layoutDirection() == Qt.RightToLeft:
            x = track_rect.right() - margin - d - self._handle_pos * travel
        else:
            x = track_rect.left() + margin + self._handle_pos * travel

        handle_rect = QRectF(x, track_rect.top() + margin, d, d)

        p.setPen(QPen(Qt.black, 0.5))
        p.setOpacity(0.08)
        p.drawEllipse(handle_rect.adjusted(0.5, 1.0, 0.5, 1.0))
        p.setOpacity(1.0)

        p.setPen(Qt.NoPen)
        p.setBrush(handleC if self.isEnabled() else disHandleC)
        p.drawEllipse(handle_rect)

        # --- NEU: Border immer zeichnen ---
        if self.hasFocus():
            # Fokus: gestrichelt + Highlight-Farbe
            pen = QPen(self.palette().color(QPalette.ColorRole.Highlight), 1.5, Qt.SolidLine)
        else:
            # Normal: fester Rahmen, z. B. MidText-Farbe
            pen = QPen(self.palette().color(QPalette.ColorRole.AlternateBase), 1.2, Qt.SolidLine)

        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(track_rect.adjusted(1, 1, -1, -1), r - 1, r - 1)

    def _colors(self):
        pal = self.palette()

        # Rollen & Gruppen IMMER über QPalette.<Role>/<Group> referenzieren
        onC = self._onColor or pal.color(QPalette.Highlight)
        # Mid ist neutral/grau; falls Theme kein brauchbares Mid liefert, auf Button umschalten
        mid = pal.color(QPalette.Mid)
        offC = self._offColor or (mid if mid.isValid() else pal.color(QPalette.Button))

        handleC = self._handleColor or pal.color(QPalette.Base)

        disTrackC = pal.color(QPalette.Disabled, QPalette.Mid)
        disHandleC = pal.color(QPalette.Disabled, QPalette.Button)

        return onC, offC, handleC, disTrackC, disHandleC

    def _update_accessible_description(self):
        self.setAccessibleDescription("Ein" if self.isChecked() else "Aus")

    # ----- Animations-Property -----
    def getHandlePos(self) -> float:
        return self._handle_pos

    def setHandlePos(self, v: float) -> None:
        v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
        if v == self._handle_pos:
            return
        self._handle_pos = v
        self.update()

    handlePos = Property(float, getHandlePos, setHandlePos)


# ---- Demo ----
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    w = QWidget()
    lay = QHBoxLayout(w)

    # lbl = QLabel("Aus")
    sw = ToggleSwitch(checked=False)
    sw.setAnimationDuration(180)
    # Farben optional:
    # sw.setOnColor(QColor("#4caf50"))
    # sw.setOffColor(QColor("#9e9e9e"))
    # sw.setHandleColor(QColor("#ffffff"))

    # sw.toggled.connect(lambda c: lbl.setText("Ein" if c else "Aus"))

    lay.addWidget(sw)
    # lay.addWidget(lbl)

    w.setWindowTitle("ToggleSwitch Demo – PySide6")
    w.resize(260, 80)
    w.show()
    sys.exit(app.exec())
