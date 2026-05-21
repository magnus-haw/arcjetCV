"""Interactive guided tour for the arcjetCV application.

Mirrors the BEAST web tour but implemented as a PySide6 overlay + card pair.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt
from PySide6.QtGui import (
    QColor, QKeyEvent, QLinearGradient, QPainter, QPainterPath, QPen,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# ---------------------------------------------------------------------------
# Step definition
# ---------------------------------------------------------------------------

@dataclass
class TourStep:
    title: str
    body: str
    widget_getter: Optional[Callable[[], Optional[QWidget]]] = None
    tab_switcher: Optional[Callable[[], None]] = None
    position: str = "bottom"  # bottom | top | right | left


# ---------------------------------------------------------------------------
# Overlay  — darkens the window with a spotlight cutout
# ---------------------------------------------------------------------------

class _TourOverlay(QWidget):
    """Semi-transparent dark overlay with a rounded spotlight cutout."""

    _PAD = 8

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._target_rect: Optional[QRect] = None
        self._on_resize: Optional[Callable[[], None]] = None
        self.resize(parent.size())
        self.raise_()

    def set_target(self, rect: Optional[QRect]) -> None:
        self._target_rect = rect
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        full = QPainterPath()
        full.addRect(0.0, 0.0, float(self.width()), float(self.height()))

        if self._target_rect is not None:
            r = self._target_rect
            p = self._PAD
            spot = QPainterPath()
            spot.addRoundedRect(
                float(r.left() - p), float(r.top() - p),
                float(r.width() + 2 * p), float(r.height() + 2 * p),
                8.0, 8.0,
            )
            path = full.subtracted(spot)
        else:
            path = full

        painter.fillPath(path, QColor(0, 0, 0, 150))

        if self._target_rect is not None:
            r = self._target_rect
            p = self._PAD
            painter.setPen(QPen(QColor(99, 132, 235, 210), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(
                r.left() - p, r.top() - p,
                r.width() + 2 * p, r.height() + 2 * p,
                8, 8,
            )

    def resizeEvent(self, event) -> None:  # noqa: N802
        if self.parent():
            self.resize(self.parent().size())
        if self._on_resize:
            self._on_resize()
        super().resizeEvent(event)


# ---------------------------------------------------------------------------
# Card  — floating tooltip with title, body, progress bar, navigation
#
# We paint the white card background ourselves (paintEvent) so the card is
# always white regardless of the application's colour theme.  All child
# container QWidgets are explicitly made transparent so they don't obscure
# this background.  Labels get their text colour via stylesheet so they are
# never affected by the palette's foreground colour.
# ---------------------------------------------------------------------------

# ── Card colour palette (matches arcjetCV dark UI) ──────────────────────────
_C_BG      = QColor(0x1E, 0x26, 0x38)   # card body  — deep navy
_C_HEADER  = QColor(0x16, 0x1D, 0x2D)   # header strip — slightly darker
_C_BORDER  = QColor(0x2D, 0x3A, 0x52)   # subtle edge
_C_ACCENT  = QColor(0x4E, 0x73, 0xDF)   # blue accent
_C_ACCENT2 = QColor(0x22, 0x4A, 0xBE)   # darker blue
_C_TEXT    = "#CBD5E1"                   # primary text (slate-300)
_C_MUTED   = "#64748B"                   # muted text  (slate-500)

_BTN_PREV = (
    "QPushButton {"
    "  font-size: 12px; font-weight: 600; padding: 6px 16px;"
    "  border-radius: 7px; border: 1px solid #2d3a52;"
    "  background: transparent; color: #94a3b8;"
    "}"
    "QPushButton:disabled { color: #3a4a62; border-color: #1e2638; }"
)

_BTN_NEXT = (
    "QPushButton {"
    "  font-size: 12px; font-weight: 600; padding: 6px 16px;"
    "  border-radius: 7px; border: 1px solid #4e73df;"
    "  background: #4e73df; color: #ffffff;"
    "}"
    "QPushButton:hover { background: #3a5ecc; border-color: #3a5ecc; }"
)

_BTN_CLOSE = (
    "QPushButton {"
    "  background: transparent; border: none;"
    "  color: rgba(255,255,255,100); font-size: 22px;"
    "}"
    "QPushButton:hover { color: white; }"
)

_TRANSPARENT = "QWidget { background: transparent; }"


class _TourCard(QWidget):
    """Floating card; always white regardless of the app colour theme."""

    _W = 390
    _HEADER_H = 54   # approximate header height (tracked after first show)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("tourCard")
        self.setFixedWidth(self._W)
        # WA_TranslucentBackground lets the rounded corners show correctly on
        # Windows without needing a WS_EX_LAYERED hack.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)
        self.raise_()

    # ── background painting ──────────────────────────────────────────────────

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        r = 12.0

        # Dark card body
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, w, h, r, r)
        painter.fillPath(path, _C_BG)

        # Subtle border
        painter.setPen(QPen(_C_BORDER, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(0.5, 0.5, w - 1, h - 1, r, r)

        # Blue gradient header strip (rounded top, square bottom)
        hh = float(self._header.height())
        grad = QLinearGradient(0, 0, w, hh)
        grad.setColorAt(0.0, _C_ACCENT)
        grad.setColorAt(1.0, _C_ACCENT2)

        header_path = QPainterPath()
        header_path.addRoundedRect(0.0, 0.0, w, hh, r, r)
        # extend bottom of header downward to fill the square bottom half
        fill_path = QPainterPath()
        fill_path.addRect(0.0, r, w, max(0.0, hh - r))
        header_path = header_path.united(fill_path)
        painter.fillPath(header_path, grad)

    # ── layout ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header (transparent bg — we paint it in paintEvent) ──────────────
        self._header = QWidget(self)
        self._header.setStyleSheet(_TRANSPARENT)
        hlay = QHBoxLayout(self._header)
        hlay.setContentsMargins(18, 12, 12, 12)
        hlay.setSpacing(8)

        self._title = QLabel("", self._header)
        self._title.setWordWrap(True)
        self._title.setStyleSheet(
            "QLabel { color: #ffffff; font-size: 13px; font-weight: 700;"
            " background: transparent; }"
        )
        hlay.addWidget(self._title, 1)

        self.close_btn = QPushButton("×", self._header)
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet(_BTN_CLOSE)
        hlay.addWidget(self.close_btn)

        outer.addWidget(self._header)

        # ── Body ─────────────────────────────────────────────────────────────
        body_wrap = QWidget(self)
        body_wrap.setStyleSheet(_TRANSPARENT)
        bl = QVBoxLayout(body_wrap)
        bl.setContentsMargins(20, 14, 20, 6)

        self._body = QLabel("", body_wrap)
        self._body.setWordWrap(True)
        self._body.setStyleSheet(
            f"QLabel {{ color: {_C_TEXT}; font-size: 12px; background: transparent; }}"
        )
        bl.addWidget(self._body)
        outer.addWidget(body_wrap)

        # ── Progress strip ───────────────────────────────────────────────────
        prog_wrap = QWidget(self)
        prog_wrap.setStyleSheet(_TRANSPARENT)
        pl = QVBoxLayout(prog_wrap)
        pl.setContentsMargins(20, 4, 20, 10)

        self._prog_bg = QWidget(prog_wrap)
        self._prog_bg.setFixedHeight(4)
        self._prog_bg.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self._prog_bg.setStyleSheet(
            "QWidget { background: #2d3a52; border-radius: 2px; }"
        )
        self._prog_fill = QWidget(self._prog_bg)
        self._prog_fill.setFixedHeight(4)
        self._prog_fill.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self._prog_fill.setStyleSheet(
            "QWidget { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #4e73df, stop:1 #818cf8); border-radius: 2px; }"
        )
        self._prog_fill.resize(0, 4)
        pl.addWidget(self._prog_bg)
        outer.addWidget(prog_wrap)

        # ── Footer ───────────────────────────────────────────────────────────
        footer = QWidget(self)
        footer.setStyleSheet(_TRANSPARENT)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 0, 20, 14)
        fl.setSpacing(8)

        self.prev_btn = QPushButton("← Back", footer)
        self.prev_btn.setStyleSheet(_BTN_PREV)
        fl.addWidget(self.prev_btn)

        fl.addStretch()

        self._counter = QLabel("", footer)
        self._counter.setStyleSheet(
            f"QLabel {{ font-size: 11px; color: {_C_MUTED}; background: transparent; }}"
        )
        fl.addWidget(self._counter)

        fl.addStretch()

        self.next_btn = QPushButton("Next →", footer)
        self.next_btn.setStyleSheet(_BTN_NEXT)
        fl.addWidget(self.next_btn)

        outer.addWidget(footer)
        self.adjustSize()

    # ── state update ─────────────────────────────────────────────────────────

    def update_step(self, title: str, body: str, idx: int, total: int) -> None:
        self._title.setText(title)
        self._body.setText(body)
        self._counter.setText(f"{idx + 1} / {total}")
        self.prev_btn.setEnabled(idx > 0)
        self.next_btn.setText("Done" if idx == total - 1 else "Next →")
        self.adjustSize()
        self._refresh_fill(idx, total)

    def _refresh_fill(self, idx: int, total: int) -> None:
        bw = self._prog_bg.width()
        if bw > 0:
            self._prog_fill.resize(int(bw * (idx + 1) / total), 4)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        try:
            parts = self._counter.text().split("/")
            idx = int(parts[0].strip()) - 1
            total = int(parts[1].strip())
            self._refresh_fill(idx, total)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Key filter installed on the main window while the tour is active
# ---------------------------------------------------------------------------

class _KeyFilter(QObject):
    def __init__(self, tour: "ArcjetCVTour") -> None:
        super().__init__()
        self._tour = tour

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()  # type: ignore[attr-defined]
            if key == Qt.Key.Key_Escape:
                self._tour.end()
                return True
            if key in (Qt.Key.Key_Right, Qt.Key.Key_Return, Qt.Key.Key_Space):
                self._tour._go(1)
                return True
            if key == Qt.Key.Key_Left:
                self._tour._go(-1)
                return True
        return False


# ---------------------------------------------------------------------------
# Tour controller
# ---------------------------------------------------------------------------

class ArcjetCVTour:
    """Interactive step-by-step tour for the arcjetCV main window."""

    _GAP = 16
    _EDGE = 8

    def __init__(self, main_window) -> None:
        self._win = main_window
        self._overlay: Optional[_TourOverlay] = None
        self._card: Optional[_TourCard] = None
        self._key_filter: Optional[_KeyFilter] = None
        self._idx: int = 0
        self._steps: List[TourStep] = self._build_steps()

    # ------------------------------------------------------------------
    # Step definitions
    # ------------------------------------------------------------------

    def _build_steps(self) -> List[TourStep]:
        ui = self._win.ui

        def tab_process():
            ui.tabWidget.setCurrentWidget(ui.tab)

        def tab_analysis():
            ui.tabWidget.setCurrentWidget(ui.tab_2)

        def tab_calibrate():
            ui.tabWidget.setCurrentWidget(ui.tab_8)

        return [
            TourStep(
                title="Welcome to arcjetCV",
                body=(
                    "arcjetCV is a NASA tool for automatically extracting material "
                    "model and bow-shock contours from arc-jet test videos. "
                    "This tour walks you through the main workflow in about 2 minutes.\n\n"
                    "Use the arrow keys or the buttons below to navigate."
                ),
            ),
            TourStep(
                title="Step 1 — Calibrate",
                body=(
                    "The Calibrate tab lets you run a checkerboard calibration "
                    "to compute the camera matrix and pixels-per-mm scale. "
                    "If you already have a calibration JSON file, you can skip "
                    "straight to loading it on the next screen."
                ),
                widget_getter=lambda: ui.tab_8,
                tab_switcher=tab_calibrate,
            ),
            TourStep(
                title="Load Calibration File",
                body=(
                    "Click 'Load Calibration' to import an existing JSON file. "
                    "arcjetCV reads pixels_per_mm, the camera matrix, distortion "
                    "coefficients, and homography from it. Once loaded, spatial "
                    "measurements are automatically converted to millimetres."
                ),
                widget_getter=lambda: ui.pushButton_loadCalibration,
                tab_switcher=tab_process,
                position="left",
            ),
            TourStep(
                title="Step 2 — Load Video",
                body=(
                    "Load an arc-jet test video or still image. Supported formats: "
                    "MP4, AVI, MOV, PNG, TIFF, and more.\n\n"
                    "The tool scans every frame to build a brightness curve, "
                    "then automatically detects the arc-on / arc-off window."
                ),
                widget_getter=lambda: ui.pushButton_loadVideo,
                tab_switcher=tab_process,
                position="left",
            ),
            TourStep(
                title="Video Preview",
                body=(
                    "The main viewport shows the current frame with segmentation "
                    "contours overlaid in real time: green for the model surface, "
                    "blue for the bow shock.\n\n"
                    "Hover anywhere on the image to read the pixel's RGB and HSV "
                    "values — useful for tuning filter thresholds."
                ),
                widget_getter=lambda: ui.Window0,
                tab_switcher=tab_process,
                position="right",
            ),
            TourStep(
                title="Brightness Timeline",
                body=(
                    "This curve shows arc-jet plasma brightness across all frames. "
                    "The red vertical line tracks the frame currently in the preview. "
                    "Green markers show the selected processing window.\n\n"
                    "Click anywhere on the curve to jump instantly to that frame."
                ),
                widget_getter=lambda: ui.Window3,
                tab_switcher=tab_process,
                position="top",
            ),
            TourStep(
                title="Input Parameters",
                body=(
                    "• Frame Index — scrub through frames one at a time\n"
                    "• Flow Direction — which way plasma flows across the frame "
                    "(right, left, up, or down); controls the sign of recession\n"
                    "• Filter Method — segmentation algorithm:\n"
                    "  CNN (deep learning), AutoHSV (auto-tuned), HSV, or GRAY"
                ),
                widget_getter=lambda: ui.groupBox_2,
                tab_switcher=tab_process,
                position="left",
            ),
            TourStep(
                title="Segmentation Filter Tabs",
                body=(
                    "Fine-tune the segmentation parameters:\n"
                    "• Crop — draw a region of interest on the image or type pixel bounds\n"
                    "• Model HSV — hue / saturation / intensity range for the test article\n"
                    "• Shock HSV — HSV range for the bow shock layer\n\n"
                    "All changes update the contour overlay in real time."
                ),
                widget_getter=lambda: ui.FilterTabs,
                tab_switcher=tab_process,
                position="left",
            ),
            TourStep(
                title="Step 3 — Process Frames",
                body=(
                    "Set First and Last Good Frame to the arc-on window visible in "
                    "the brightness plot. 'Frame Skips' processes every Nth frame "
                    "for speed — N=5 is a good default.\n\n"
                    "Enable 'Write Video' to save an annotated output video. "
                    "Then click 'Process All' to start."
                ),
                widget_getter=lambda: ui.groupBox,
                tab_switcher=tab_process,
                position="left",
            ),
            TourStep(
                title="Progress Bar",
                body=(
                    "Processing runs in a background thread so the UI stays "
                    "responsive. The bar fills as frames are analysed.\n\n"
                    "When complete, a JSON file with all contour data is written "
                    "to the same folder as the input video."
                ),
                widget_getter=lambda: ui.progressBar,
                tab_switcher=tab_process,
                position="top",
            ),
            TourStep(
                title="Step 4 — Analyse Results",
                body=(
                    "Switch to the Analysis tab to load output files and visualise "
                    "results. You can combine JSON files from multiple test runs "
                    "into a single overlay plot."
                ),
                widget_getter=lambda: ui.tab_2,
                tab_switcher=tab_analysis,
            ),
            TourStep(
                title="Load Output Files",
                body=(
                    "Click 'Load Files' to open one or more JSON output files "
                    "produced during processing. The data summary label shows "
                    "total frame count, calibration resolution, and the folder path."
                ),
                widget_getter=lambda: ui.pushButton_LoadFiles,
                tab_switcher=tab_analysis,
                position="left",
            ),
            TourStep(
                title="XY Shape Evolution",
                body=(
                    "The left panel overlays model contour profiles across time:\n"
                    "• Red — initial (first) profile\n"
                    "• Green — maximum expansion profile\n"
                    "• Blue — final profile\n\n"
                    "This gives an immediate visual of material recession or swelling "
                    "during the arc-jet exposure."
                ),
                widget_getter=lambda: ui.Window1,
                tab_switcher=tab_analysis,
                position="right",
            ),
            TourStep(
                title="XT Time-Series",
                body=(
                    "The right panel plots selected metrics versus time: model "
                    "surface position, shock standoff, radii at ±50 % and ±95 % "
                    "of the radius, and more.\n\n"
                    "A recession-start marker and linear fit are drawn automatically "
                    "when 'Model Center' is enabled."
                ),
                widget_getter=lambda: ui.Window2,
                tab_switcher=tab_analysis,
                position="left",
            ),
            TourStep(
                title="Plot Options",
                body=(
                    "Toggle which quantities appear in the time-series plot. "
                    "'Kalman Filter' smooths noisy signals. "
                    "The units combo switches between pixels and millimetres "
                    "(requires a calibration file to have been loaded).\n\n"
                    "Use the Fit tab to restrict the linear fit to a sub-interval."
                ),
                widget_getter=lambda: ui.groupBox_XT_params,
                tab_switcher=tab_analysis,
                position="left",
            ),
            TourStep(
                title="Export to CSV",
                body=(
                    "Click 'Export CSV' to save all time-series data, linear fit "
                    "parameters, and PNG plot images to a folder of your choice."
                ),
                widget_getter=lambda: ui.pushButton_export_csv,
                tab_switcher=tab_analysis,
                position="left",
            ),
            TourStep(
                title="You're all set!",
                body=(
                    "That covers the full arcjetCV workflow:\n"
                    "Calibrate → Load Video → Process → Analyse → Export.\n\n"
                    "Hover any control to see a tooltip. "
                    "Restart this tour at any time from Help → Start Tour."
                ),
            ),
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._teardown()
        self._idx = 0
        self._mount()
        self._render()

    def end(self) -> None:
        self._teardown()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _teardown(self) -> None:
        if self._key_filter is not None:
            self._win.removeEventFilter(self._key_filter)
            self._key_filter = None
        if self._overlay is not None:
            self._overlay.hide()
            self._overlay.deleteLater()
            self._overlay = None
        if self._card is not None:
            self._card.hide()
            self._card.deleteLater()
            self._card = None

    def _mount(self) -> None:
        self._overlay = _TourOverlay(self._win)
        self._overlay._on_resize = self._on_window_resize
        self._overlay.show()

        self._card = _TourCard(self._win)
        self._card.close_btn.clicked.connect(self.end)
        self._card.prev_btn.clicked.connect(lambda: self._go(-1))
        self._card.next_btn.clicked.connect(lambda: self._go(1))
        self._card.show()
        self._card.raise_()

        self._key_filter = _KeyFilter(self)
        self._win.installEventFilter(self._key_filter)

    def _on_window_resize(self) -> None:
        if self._card is None or self._overlay is None:
            return
        step = self._steps[self._idx]
        target = self._get_target(step)
        if target is not None:
            rect = self._widget_rect_in_overlay(target)
            self._overlay.set_target(rect)
            self._place_card(rect, step.position)
        else:
            self._overlay.set_target(None)
            self._center_card()
        self._card.raise_()

    def _go(self, delta: int) -> None:
        n = self._idx + delta
        if n >= len(self._steps):
            self.end()
            return
        if n < 0:
            return
        self._idx = n
        self._render()

    def _render(self) -> None:
        step = self._steps[self._idx]

        if step.tab_switcher is not None:
            step.tab_switcher()
            QApplication.processEvents()

        self._card.update_step(step.title, step.body, self._idx, len(self._steps))

        target = self._get_target(step)

        if target is not None and target.isVisible():
            rect = self._widget_rect_in_overlay(target)
            self._overlay.set_target(rect)
            self._place_card(rect, step.position)
        else:
            self._overlay.set_target(None)
            self._center_card()

        self._overlay.raise_()
        self._card.raise_()

    def _get_target(self, step: TourStep) -> Optional[QWidget]:
        if step.widget_getter is None:
            return None
        try:
            return step.widget_getter()
        except Exception:
            return None

    def _widget_rect_in_overlay(self, widget: QWidget) -> QRect:
        global_pos = widget.mapToGlobal(QPoint(0, 0))
        local_pos = self._overlay.mapFromGlobal(global_pos)
        return QRect(local_pos, widget.size())

    def _place_card(self, target_rect: QRect, position: str) -> None:
        card = self._card
        GAP = self._GAP
        EDGE = self._EDGE
        p = _TourOverlay._PAD

        pad_rect = target_rect.adjusted(-p, -p, p, p)

        cw = card.width()
        ch = card.height()
        ww = self._win.width()
        wh = self._win.height()

        cx = pad_rect.left() + pad_rect.width() // 2
        left = max(EDGE, min(cx - cw // 2, ww - cw - EDGE))

        if position == "top":
            top = pad_rect.top() - GAP - ch
            if top < EDGE:
                top = pad_rect.bottom() + GAP
        elif position == "right":
            left = min(pad_rect.right() + GAP, ww - cw - EDGE)
            top = max(EDGE, min(
                pad_rect.top() + pad_rect.height() // 2 - ch // 2,
                wh - ch - EDGE,
            ))
        elif position == "left":
            left = max(EDGE, pad_rect.left() - GAP - cw)
            top = max(EDGE, min(
                pad_rect.top() + pad_rect.height() // 2 - ch // 2,
                wh - ch - EDGE,
            ))
        else:  # bottom (default)
            top = pad_rect.bottom() + GAP
            if top + ch > wh - EDGE:
                top = pad_rect.top() - GAP - ch

        card.move(max(EDGE, left), max(EDGE, top))

    def _center_card(self) -> None:
        card = self._card
        x = (self._win.width() - card.width()) // 2
        y = (self._win.height() - card.height()) // 2
        card.move(x, y)
