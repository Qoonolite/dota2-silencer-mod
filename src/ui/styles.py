DARK_THEME = """
/* Базовые стили Steam */
QWidget {
    background-color: #1b2838;
    color: #c7d5e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QMainWindow {
    background-color: #1b2838;
}

QDialog {
    background-color: #1b2838;
}

/* Заголовки */
QLabel {
    color: #c7d5e0;
    background-color: transparent;
}

/* Кнопки */
QPushButton {
    background-color: #2a475e;
    color: #c7d5e0;
    border: 1px solid #3d6a8e;
    border-radius: 2px;
    padding: 10px 20px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #3d6a8e;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #66c0f4;
    color: #1b2838;
}

/* Главная кнопка */
QPushButton#primary {
    background-color: #7ea640;
    color: #ffffff;
    border: 1px solid #5a7a2e;
    border-bottom: 3px solid #4a6525;
    border-radius: 3px;
    font-weight: bold;
    font-size: 18px;
    padding: 18px 36px;
}

QPushButton#primary:hover {
    background-color: #8fb848;
    border-color: #6a8a35;
    border-bottom-color: #5a7a2e;
}

QPushButton#primary:pressed {
    background-color: #6d9235;
    border-bottom: 1px solid #4a6525;
}

/* Чекбоксы */
QCheckBox {
    color: #c7d5e0;
    spacing: 12px;
    font-size: 15px;
    padding: 10px;
}

QCheckBox:hover {
    color: #66c0f4;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid #3d6a8e;
    border-radius: 3px;
    background-color: #1b2838;
}

QCheckBox::indicator:hover {
    border-color: #66c0f4;
}

QCheckBox::indicator:checked {
    background-color: #7ea640;
    border: 2px solid #5a7a2e;
    border-radius: 3px;
}

/* Поля ввода */
QLineEdit {
    background-color: #2a475e;
    color: #c7d5e0;
    border: 1px solid #3d6a8e;
    border-radius: 2px;
    padding: 10px 14px;
    font-size: 14px;
}

QLineEdit:focus {
    border-color: #66c0f4;
}

QLineEdit:read-only {
    background-color: #1b2838;
    color: #8f98a0;
}

/* Группы */
QGroupBox {
    border: 1px solid #3d6a8e;
    border-radius: 4px;
    margin-top: 20px;
    padding-top: 25px;
    font-weight: bold;
    font-size: 16px;
    color: #66c0f4;
    background-color: #1b2838;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    color: #66c0f4;
    font-size: 16px;
    font-weight: bold;
}

/* Прогресс-бар */
QProgressBar {
    border: 1px solid #3d6a8e;
    border-radius: 2px;
    text-align: center;
    background-color: #2a475e;
    color: #c7d5e0;
    font-weight: bold;
    height: 28px;
}

QProgressBar::chunk {
    background-color: #66c0f4;
    border-radius: 2px;
}

/* Статус-бар */
QStatusBar {
    background-color: #171a21;
    color: #8f98a0;
    border-top: 1px solid #3d6a8e;
    font-size: 13px;
}

/* Скроллбары */
QScrollBar:vertical {
    background-color: #2a475e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #3d6a8e;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #66c0f4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2a475e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #3d6a8e;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #66c0f4;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""