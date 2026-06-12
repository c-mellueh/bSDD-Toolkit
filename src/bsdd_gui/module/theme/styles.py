"""Design tokens and QSS template for the application theme.

Both token dicts must define the same keys; the QSS template is rendered with
string.Template ($name placeholders) so literal QSS braces need no escaping.
Icon tokens (icon_*) are added at runtime by tool.Theme with paths to SVGs
that are tinted with the active palette.
"""

LIGHT_TOKENS = {
    "window": "#F3F4F6",
    "surface": "#FFFFFF",
    "surface_alt": "#F7F8FA",
    "surface_sunken": "#E9EBEE",
    "header": "#EDEFF2",
    "text": "#22272E",
    "text_muted": "#66707B",
    "text_disabled": "#A8B0B9",
    "border": "#D5DAE0",
    "border_strong": "#B9C1CA",
    "button": "#F6F7F9",
    "button_hover": "#ECEFF2",
    "button_pressed": "#E1E5EA",
    "accent": "#0F6E84",
    "accent_hover": "#0C5D70",
    "accent_pressed": "#0A4F60",
    "accent_soft": "#DCEEF2",
    "on_accent": "#FFFFFF",
    "tooltip_bg": "#262B31",
    "tooltip_text": "#F2F4F6",
    "scroll_handle": "#C5CCD4",
    "scroll_handle_hover": "#ABB4BE",
    "link": "#0F6E84",
    "error": "#C0392B",
}

DARK_TOKENS = {
    "window": "#24282F",
    "surface": "#1B1F25",
    "surface_alt": "#20242B",
    "surface_sunken": "#15181D",
    "header": "#272C34",
    "text": "#E7EAEE",
    "text_muted": "#9AA4AF",
    "text_disabled": "#5B636D",
    "border": "#3A414B",
    "border_strong": "#4B545F",
    "button": "#2D333C",
    "button_hover": "#353D47",
    "button_pressed": "#3E4853",
    "accent": "#4FC1D2",
    "accent_hover": "#66CBDA",
    "accent_pressed": "#3DAEBF",
    "accent_soft": "#1F3E45",
    "on_accent": "#0C1418",
    "tooltip_bg": "#E7EAEE",
    "tooltip_text": "#24282F",
    "scroll_handle": "#424A55",
    "scroll_handle_hover": "#525C68",
    "link": "#5CC7D6",
    "error": "#E06055",
}

# SVG sources for QSS image: url(...) sub-controls; tinted at runtime.
SVG_TEMPLATES = {
    "chevron_down": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
        '<path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="$color" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    ),
    "chevron_up": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
        '<path d="M2.5 7.5 6 4l3.5 3.5" fill="none" stroke="$color" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    ),
    "chevron_right": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
        '<path d="M4.5 2.5 8 6l-3.5 3.5" fill="none" stroke="$color" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    ),
    "check": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">'
        '<path d="M2.5 6.5 5 9l4.5-5.5" fill="none" stroke="$color" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    ),
}

QSS_TEMPLATE = """
/* ---- base ------------------------------------------------------------ */
QWidget {
    color: $text;
}
QMainWindow, QDialog {
    background-color: $window;
}
QWidget:disabled {
    color: $text_disabled;
}
QToolTip {
    background-color: $tooltip_bg;
    color: $tooltip_text;
    border: 1px solid $border_strong;
    padding: 5px 8px;
}

/* ---- menus ----------------------------------------------------------- */
QMenuBar {
    background-color: $window;
    border-bottom: 1px solid $border;
    padding: 2px 4px;
}
QMenuBar::item {
    padding: 4px 10px;
    border-radius: 4px;
    background: transparent;
}
QMenuBar::item:selected {
    background-color: $accent_soft;
}
QMenuBar::item:pressed {
    background-color: $accent_soft;
    color: $accent;
}
QMenu {
    background-color: $surface;
    border: 1px solid $border;
    padding: 5px;
}
QMenu::item {
    padding: 5px 24px 5px 10px;
    border-radius: 4px;
    margin: 1px 2px;
}
QMenu::item:selected {
    background-color: $accent_soft;
}
QMenu::item:disabled {
    color: $text_disabled;
    background: transparent;
}
QMenu::separator {
    height: 1px;
    background-color: $border;
    margin: 5px 8px;
}
QMenu::icon {
    padding-left: 8px;
}

/* ---- buttons ---------------------------------------------------------- */
QPushButton {
    background-color: $button;
    border: 1px solid $border_strong;
    border-radius: 6px;
    padding: 5px 14px;
    min-height: 18px;
}
QPushButton:hover {
    background-color: $button_hover;
}
QPushButton:pressed {
    background-color: $button_pressed;
}
QPushButton:focus {
    border-color: $accent;
}
QPushButton:default {
    background-color: $accent;
    border-color: $accent;
    color: $on_accent;
}
QPushButton:default:hover {
    background-color: $accent_hover;
    border-color: $accent_hover;
}
QPushButton:default:pressed {
    background-color: $accent_pressed;
}
QPushButton:disabled {
    background-color: $surface_sunken;
    border-color: $border;
    color: $text_disabled;
}
QToolButton {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px;
}
QToolButton:hover {
    background-color: $button_hover;
}
QToolButton:pressed,
QToolButton:checked {
    background-color: $accent_soft;
}

/* ---- inputs ------------------------------------------------------------ */
QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: 6px;
    padding: 4px 8px;
    selection-background-color: $accent;
    selection-color: $on_accent;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QAbstractSpinBox:focus, QComboBox:focus {
    border-color: $accent;
}
QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled,
QAbstractSpinBox:disabled, QComboBox:disabled {
    background-color: $surface_sunken;
    color: $text_disabled;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: url("$icon_chevron_down");
    width: 12px;
    height: 12px;
}
QComboBox QAbstractItemView {
    background-color: $surface;
    border: 1px solid $border;
    padding: 4px;
    selection-background-color: $accent_soft;
    selection-color: $text;
}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
    border: none;
    width: 18px;
    background: transparent;
}
QAbstractSpinBox::up-arrow {
    image: url("$icon_chevron_up");
    width: 10px;
    height: 10px;
}
QAbstractSpinBox::down-arrow {
    image: url("$icon_chevron_down");
    width: 10px;
    height: 10px;
}

/* ---- check / radio ------------------------------------------------------ */
QCheckBox, QRadioButton {
    spacing: 7px;
    background: transparent;
}
QCheckBox::indicator, QGroupBox::indicator, QTreeView::indicator,
QTableView::indicator, QListView::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid $border_strong;
    border-radius: 4px;
    background-color: $surface;
}
QCheckBox::indicator:hover, QGroupBox::indicator:hover {
    border-color: $accent;
}
QCheckBox::indicator:checked, QGroupBox::indicator:checked,
QTreeView::indicator:checked, QTableView::indicator:checked,
QListView::indicator:checked {
    background-color: $accent;
    border-color: $accent;
    image: url("$icon_check");
}
QCheckBox::indicator:disabled, QGroupBox::indicator:disabled {
    background-color: $surface_sunken;
    border-color: $border;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid $border_strong;
    border-radius: 8px;
    background-color: $surface;
}
QRadioButton::indicator:hover {
    border-color: $accent;
}
QRadioButton::indicator:checked {
    border-color: $accent;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 $accent, stop:0.55 $accent, stop:0.65 $surface, stop:1 $surface);
}

/* ---- item views ---------------------------------------------------------- */
QTreeView, QTableView, QListView {
    background-color: $surface;
    alternate-background-color: $surface_alt;
    border: 1px solid $border;
    border-radius: 6px;
    outline: 0;
    selection-background-color: $accent;
    selection-color: $on_accent;
}
QTreeView::item, QTableView::item, QListView::item {
    padding: 3px 4px;
}
QTreeView::item:selected, QTableView::item:selected, QListView::item:selected {
    background-color: $accent;
    color: $on_accent;
}
QTreeView::item:selected:!active, QTableView::item:selected:!active,
QListView::item:selected:!active {
    background-color: $accent_soft;
    color: $text;
}
QTreeView::item:hover:!selected, QListView::item:hover:!selected {
    background-color: $surface_alt;
}
QTreeView::branch {
    background: transparent;
}
QTreeView::branch:has-children:closed {
    image: url("$icon_chevron_right");
}
QTreeView::branch:has-children:open {
    image: url("$icon_chevron_down");
}
QTableView {
    gridline-color: $border;
}
QHeaderView {
    background-color: $header;
    border: none;
}
QHeaderView::section {
    background-color: $header;
    color: $text_muted;
    padding: 5px 8px;
    border: none;
    border-right: 1px solid $border;
    border-bottom: 1px solid $border;
}
QHeaderView::section:last {
    border-right: none;
}
QHeaderView::down-arrow {
    image: url("$icon_chevron_down");
    width: 10px;
    height: 10px;
    subcontrol-position: center right;
    right: 4px;
}
QHeaderView::up-arrow {
    image: url("$icon_chevron_up");
    width: 10px;
    height: 10px;
    subcontrol-position: center right;
    right: 4px;
}
QTableCornerButton::section {
    background-color: $header;
    border: none;
    border-right: 1px solid $border;
    border-bottom: 1px solid $border;
}

/* ---- tabs ------------------------------------------------------------------ */
QTabWidget::pane {
    border: 1px solid $border;
    border-radius: 6px;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: $text_muted;
    padding: 6px 14px;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}
QTabBar::tab:hover {
    color: $text;
}
QTabBar::tab:selected {
    color: $text;
    border-bottom: 2px solid $accent;
}

/* ---- toolbox (settings) ------------------------------------------------------ */
QToolBox::tab {
    background-color: $button;
    border: 1px solid $border;
    border-radius: 6px;
    padding: 5px;
    color: $text_muted;
}
QToolBox::tab:hover {
    background-color: $button_hover;
    color: $text;
}
QToolBox::tab:selected {
    color: $accent;
    font-weight: 600;
}

/* ---- containers --------------------------------------------------------------- */
QGroupBox {
    border: 1px solid $border;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0px 4px;
    color: $text_muted;
}
QSplitter::handle {
    background-color: $window;
}
QSplitter::handle:hover {
    background-color: $accent_soft;
}
QToolBar {
    background-color: $window;
    border-bottom: 1px solid $border;
    padding: 3px;
    spacing: 3px;
}
QStatusBar {
    background-color: $window;
    border-top: 1px solid $border;
    color: $text_muted;
}
QStatusBar::item {
    border: none;
}
QDockWidget::title {
    background-color: $header;
    padding: 5px 8px;
}

/* ---- scrollbars ------------------------------------------------------------------ */
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background-color: $scroll_handle;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: $scroll_handle_hover;
}
QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background-color: $scroll_handle;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: $scroll_handle_hover;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}
QAbstractScrollArea::corner {
    background: transparent;
}

/* ---- misc ------------------------------------------------------------------------- */
QProgressBar {
    background-color: $surface_sunken;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: $text;
}
QProgressBar::chunk {
    background-color: $accent;
    border-radius: 6px;
}
QSlider::groove:horizontal {
    height: 4px;
    background-color: $surface_sunken;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background-color: $accent;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background-color: $accent_hover;
}

/* ---- validation (see tool.Util.set_invalid) ----------------------------------------- */
QLineEdit[invalid="true"], QComboBox[invalid="true"],
QTextEdit[invalid="true"], QPlainTextEdit[invalid="true"],
QAbstractSpinBox[invalid="true"] {
    border: 1px solid $error;
}
QCheckBox[invalid="true"]::indicator {
    border-color: $error;
}
"""
