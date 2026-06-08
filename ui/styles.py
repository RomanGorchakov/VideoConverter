APP_STYLE = """
/* =========================
   GLOBAL
========================= */

QWidget {
    background-color: #1e1e2e;
    color: #f5f5f5;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QMainWindow {
    background-color: #181825;
}

/* =========================
   BUTTONS
========================= */

QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 14px;
    color: #ffffff;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #45475a;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton:disabled {
    background-color: #2b2b35;
    color: #777777;
}

/* SUCCESS BUTTON */

QPushButton#successButton {
    background-color: #2e7d32;
    border: 1px solid #388e3c;
}

QPushButton#successButton:hover {
    background-color: #388e3c;
}

/* DANGER BUTTON */

QPushButton#dangerButton {
    background-color: #c62828;
    border: 1px solid #d32f2f;
}

QPushButton#dangerButton:hover {
    background-color: #d32f2f;
}

/* WARNING BUTTON */

QPushButton#warningButton {
    background-color: #ef6c00;
    border: 1px solid #fb8c00;
}

QPushButton#warningButton:hover {
    background-color: #fb8c00;
}

/* =========================
   INPUT FIELDS
========================= */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QDoubleSpinBox,
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
    color: white;
}

QLineEdit:focus,
QTextEdit:focus,
QComboBox:focus {
    border: 1px solid #89b4fa;
}

/* =========================
   COMBOBOX
========================= */

QComboBox {
    padding-right: 25px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #89b4fa;
    color: white;
}

/* =========================
   TABLES
========================= */

QTableWidget,
QTableView {
    background-color: #11111b;
    alternate-background-color: #181825;
    border: 1px solid #313244;
    gridline-color: #45475a;
    selection-background-color: #89b4fa;
    selection-color: black;
}

QHeaderView::section {
    background-color: #313244;
    color: white;
    padding: 8px;
    border: 1px solid #45475a;
    font-weight: bold;
}

/* =========================
   PROGRESS BAR
========================= */

QProgressBar {
    border: 1px solid #45475a;
    border-radius: 8px;
    text-align: center;
    background-color: #313244;
    color: white;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 8px;
}

/* =========================
   LABELS
========================= */

QLabel {
    color: #f5f5f5;
}

/* =========================
   GROUP BOX
========================= */

QGroupBox {
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: bold;
    padding: 10px;
}

QGroupBox:title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

/* =========================
   MENU BAR
========================= */

QMenuBar {
    background-color: #181825;
    color: white;
}

QMenuBar::item:selected {
    background-color: #313244;
}

QMenu {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
}

QMenu::item:selected {
    background-color: #89b4fa;
    color: black;
}

/* =========================
   TOOLBAR
========================= */

QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    spacing: 8px;
}

/* =========================
   SCROLLBAR
========================= */

QScrollBar:vertical {
    background: #1e1e2e;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #585b70;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #6c7086;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #1e1e2e;
    height: 12px;
}

QScrollBar::handle:horizontal {
    background: #585b70;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #6c7086;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* =========================
   STATUS BAR
========================= */

QStatusBar {
    background-color: #181825;
    color: #cdd6f4;
    border-top: 1px solid #313244;
}

/* =========================
   TAB WIDGET
========================= */

QTabWidget::pane {
    border: 1px solid #45475a;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: white;
    padding: 8px 14px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #89b4fa;
    color: black;
}

/* =========================
   CHECKBOX
========================= */

QCheckBox {
    spacing: 6px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border: 1px solid #89b4fa;
    border-radius: 4px;
}

QCheckBox::indicator:unchecked {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
}

/* =========================
   SLIDER
========================= */

QSlider::groove:horizontal {
    border: 1px solid #45475a;
    height: 8px;
    background: #313244;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #89b4fa;
    border: 1px solid #89b4fa;
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}
"""


def get_style():
    """
    Возвращает глобальную тему приложения.
    """
    return APP_STYLE