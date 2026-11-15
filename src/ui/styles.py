DARK_THEME = """
/* ===== Google Material 3 — тёмно-серая тема ===== */
* {
    font-family: "Google Sans", "Roboto", "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: #202124;
    color: #e3e3e3;
}

QMainWindow, QDialog {
    background-color: #202124;
}

/* ===== Текст ===== */
QLabel {
    background: transparent;
    color: #e3e3e3;
}

QLabel#title {
    font-size: 24px;
    font-weight: 500;
    color: #e8eaed;
}

QLabel#subtitle {
    font-size: 13px;
    color: #9aa0a6;
}

QLabel#warnLabel {
    color: #fdd663;
    background-color: #3a3226;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 12px;
}

QLabel#statusDot {
    font-size: 14px;
}

QLabel#statusLabel {
    color: #9aa0a6;
    font-size: 12px;
}

/* ===== Кнопки: outlined (M3) ===== */
QPushButton {
    background-color: transparent;
    color: #a8c7fa;
    border: 1px solid #8e918f;
    border-radius: 18px;
    padding: 8px 20px;
}

QPushButton:hover {
    background-color: rgba(168, 199, 250, 0.08);
    border-color: #a8c7fa;
}

QPushButton:pressed {
    background-color: rgba(168, 199, 250, 0.16);
}

QPushButton:disabled {
    color: #5f6368;
    border-color: #3c4043;
    background-color: transparent;
}

/* ===== Главная кнопка: filled (M3) ===== */
QPushButton#primary {
    background-color: #a8c7fa;
    border: none;
    border-radius: 25px;
    color: #062e6f;
    font-size: 16px;
    font-weight: 600;
    padding: 12px 24px;
}

QPushButton#primary:hover {
    background-color: #c2d7fc;
}

QPushButton#primary:pressed {
    background-color: #8ab4f8;
}

QPushButton#primary:disabled {
    background-color: #3c4043;
    color: #8e918f;
}

/* ===== Поля ввода: капсула как поиск Google ===== */
QLineEdit {
    background-color: #303134;
    color: #e8eaed;
    border: 1px solid #3c4043;
    border-radius: 18px;
    padding: 8px 16px;
    selection-background-color: #a8c7fa;
    selection-color: #062e6f;
}

QLineEdit:focus {
    border-color: #a8c7fa;
    background-color: #35373a;
}

QLineEdit:read-only {
    color: #9aa0a6;
}

/* ===== Лог: консоль на самой тёмной поверхности ===== */
QTextEdit#logView {
    background-color: #131314;
    border: 1px solid #3c4043;
    border-radius: 12px;
    padding: 8px 10px;
    font-family: "Cascadia Mono", "Consolas", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: #a8c7fa;
    selection-color: #062e6f;
}

/* ===== Карточки: поверхность без рамки ===== */
QGroupBox {
    border: none;
    border-radius: 16px;
    margin-top: 16px;
    padding-top: 14px;
    background-color: #282a2c;
    color: #9aa0a6;
    font-weight: 500;
    font-size: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #9aa0a6;
}

/* ===== Прогресс-бар: капсула ===== */
QProgressBar {
    background-color: #444746;
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: #062e6f;
    font-size: 10px;
}

QProgressBar::chunk {
    background-color: #a8c7fa;
    border-radius: 6px;
}

/* ===== Подвал ===== */
QWidget#authorCard {
    background-color: #282a2c;
    border: none;
    border-radius: 16px;
}

QLabel#authorName {
    color: #9aa0a6;
    font-size: 12px;
    font-weight: 500;
}

/* ===== Чекбоксы ===== */
QCheckBox {
    spacing: 10px;
    padding: 6px;
}

QCheckBox:hover {
    color: #a8c7fa;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #8e918f;
    border-radius: 4px;
    background-color: transparent;
}

QCheckBox::indicator:hover {
    border-color: #a8c7fa;
}

QCheckBox::indicator:checked {
    background-color: #a8c7fa;
    border-color: #a8c7fa;
}

/* ===== Статус-бар ===== */
QStatusBar {
    background-color: #131314;
    color: #9aa0a6;
    border-top: 1px solid #3c4043;
    font-size: 12px;
}

/* ===== Подсказки ===== */
QToolTip {
    background-color: #303134;
    color: #e8eaed;
    border: 1px solid #5f6368;
    border-radius: 8px;
    padding: 6px 10px;
}

/* ===== Скроллбары ===== */
QScrollBar:vertical {
    background-color: transparent;
    width: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #5f6368;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9aa0a6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 10px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background-color: #5f6368;
    border-radius: 5px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #9aa0a6;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""
