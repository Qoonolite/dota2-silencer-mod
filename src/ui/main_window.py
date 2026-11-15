import html
import traceback
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QLineEdit,
                             QMessageBox, QTextEdit, QProgressBar,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from core.path_finder import PathFinder
from ui.path_dialog import PathDialog
from utils.config import Config
from utils.logger import GUILogger

CATEGORIES = {
    "wheel_sounds": [
        "sounds/talentcontent/**/*.vsnd_c",
        "sounds/teamfancontent/**/*.vsnd_c",
        "sounds/misc/chatwheel/**/*.vsnd_c",
        "sounds/misc/soundboard/**/*.vsnd_c",
        "sounds/misc/crownfall/**/*.vsnd_c",
    ]
}

LOG_COLORS = {
    "info": "#bdc1c6",
    "warning": "#fdd663",
    "error": "#f28b82",
    "success": "#81c995",
    "progress": "#a8c7fa",
}

STATUS_COLORS = {
    "idle": "#9aa0a6",
    "busy": "#a8c7fa",
    "ok": "#81c995",
    "error": "#f28b82",
}


def _assets_dir() -> Path:
    return Path(__file__).parent.parent / "assets"


class ProcessWorker(QThread):
    """Выполняет обработку в фоне, чтобы окно не зависало."""
    progress_changed = pyqtSignal(int, int)
    finished_ok = pyqtSignal(bool)

    def __init__(self, dota_path: str, parent=None):
        super().__init__(parent)
        self.dota_path = dota_path

    def run(self):
        log = GUILogger()
        try:
            from core.processor import SoundProcessor
            processor = SoundProcessor(Path(self.dota_path), "russian", log)
            ok = processor.process_categories(
                ["wheel_sounds"], CATEGORIES,
                on_progress=lambda cur, total: self.progress_changed.emit(cur, total)
            )
        except Exception as e:
            log.error(f"Критическая ошибка: {e}")
            log.error(traceback.format_exc())
            ok = False
        self.finished_ok.emit(ok)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.log = GUILogger()
        self.path_finder = PathFinder()
        self._worker = None
        self.log.message.connect(self._on_log_message)
        self._init_ui()
        self._init_path()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 18, 20, 16)

        # --- Шапка: иконка + название ---
        header = QHBoxLayout()
        header.setSpacing(14)

        icon_label = QLabel()
        icon_path = _assets_dir() / "app_icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(
                48, 48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(48, 48)
        header.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Dota 2 Silencer")
        title.setObjectName("title")
        subtitle = QLabel("Отключение звуковых фраз колеса чата")
        subtitle.setObjectName("subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col, stretch=1)

        version = QLabel("v2.0")
        version.setObjectName("subtitle")
        header.addWidget(version, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(header)

        warn_label = QLabel(
            "⚠  Мод работает только с русской озвучкой игры "
            "(AudioLanguage = russian в настройках Dota 2)."
        )
        warn_label.setObjectName("warnLabel")
        warn_label.setWordWrap(True)
        main_layout.addWidget(warn_label)

        path_group = QGroupBox("Папка игры")
        self._add_shadow(path_group)
        path_layout = QHBoxLayout(path_group)
        path_layout.setSpacing(8)
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Путь не найден — нажмите «Изменить»")
        self.path_input.setMinimumHeight(34)
        self.btn_change_path = QPushButton("Изменить")
        self.btn_change_path.clicked.connect(self._on_change_path)
        self.btn_change_path.setMinimumWidth(100)
        path_layout.addWidget(self.path_input, stretch=1)
        path_layout.addWidget(self.btn_change_path)
        main_layout.addWidget(path_group)

        self.btn_start = QPushButton("ПРИМЕНИТЬ МОД")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self._on_start)
        self.btn_start.setMinimumHeight(50)
        main_layout.addWidget(self.btn_start)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(10)
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDot")
        self.status_dot.setStyleSheet(f"color: {STATUS_COLORS['idle']};")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Готов к работе")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        progress_row.addWidget(self.status_dot)
        progress_row.addWidget(self.progress_bar, stretch=1)
        progress_row.addWidget(self.status_label)
        main_layout.addLayout(progress_row)

        log_group = QGroupBox("Консоль")
        self._add_shadow(log_group)
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(8, 14, 8, 8)
        self.log_view = QTextEdit()
        self.log_view.setObjectName("logView")
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        main_layout.addWidget(log_group, stretch=1)

        author_frame = QWidget()
        author_frame.setObjectName("authorCard")
        author_layout = QHBoxLayout(author_frame)
        author_layout.setContentsMargins(12, 8, 12, 8)
        author_layout.setSpacing(16)

        author_label = QLabel("Автор: Qoonolite")
        author_label.setObjectName("authorName")
        author_layout.addWidget(author_label)
        author_layout.addStretch()

        profile_link = QLabel('<a href="https://steamcommunity.com/id/Qnlite/" style="color: #a8c7fa; text-decoration: none;">Профиль Steam</a>')
        profile_link.setOpenExternalLinks(True)
        author_layout.addWidget(profile_link)

        donate_link = QLabel(
            '<a href="https://www.donationalerts.com/r/qoonolite" style="color: #fdd663; font-weight: bold; text-decoration: none;">Поддержать ♥</a>'
        )
        donate_link.setOpenExternalLinks(True)
        author_layout.addWidget(donate_link)

        main_layout.addWidget(author_frame)

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 60))
        widget.setGraphicsEffect(shadow)

    def _set_status(self, text: str, state: str = "idle"):
        self.status_label.setText(text)
        self.status_dot.setStyleSheet(f"color: {STATUS_COLORS.get(state, STATUS_COLORS['idle'])};")

    def _init_path(self):
        saved_path = self.config.get("dota_path")
        if saved_path and PathFinder.validate_user_path(Path(saved_path)):
            self.path_input.setText(saved_path)
            return
        found = self.path_finder.find()
        if found:
            self.path_input.setText(str(found))
            self.config.set("dota_path", str(found))
        else:
            self._on_change_path()

    def _on_change_path(self):
        dialog = PathDialog(self)
        if dialog.exec():
            path = dialog.selected_path
            self.path_input.setText(str(path))
            self.config.set("dota_path", str(path))

    def _on_start(self):
        dota_path = self.path_input.text()
        if not dota_path or not PathFinder.validate_user_path(Path(dota_path)):
            QMessageBox.warning(self, "Ошибка", "Укажите корректный путь к Dota 2")
            return

        self.log_view.clear()
        self._set_busy(True)
        self.progress_bar.setRange(0, 0)  # режим «занято», пока идёт поиск
        self.progress_bar.setVisible(True)
        self._set_status("Поиск файлов в архиве...", "busy")

        self._worker = ProcessWorker(dota_path, self)
        self._worker.progress_changed.connect(self._on_progress)
        self._worker.finished_ok.connect(lambda ok: self._on_finished(ok, dota_path))
        self._worker.start()

    def _on_progress(self, current: int, total: int):
        if self.progress_bar.maximum() != total:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(current)
        self._set_status(f"Упаковка: {current}/{total}", "busy")

    def _on_finished(self, success: bool, dota_path: str):
        self._set_busy(False)
        self.progress_bar.setRange(0, 100)

        if success:
            self.progress_bar.setValue(100)
            self._set_status("Готово — перезапустите Dota 2", "ok")
            lang_folder = Path(dota_path) / "game" / "dota_russian"
            msg = (
                f"✅ Обработка успешно завершена!\n\n"
                f"📁 Создан архив: {lang_folder}\\pak02_dir.vpk\n\n"
                f"Звуковые фразы колеса чата отключены для русской версии игры.\n"
                f"Никаких дополнительных параметров запуска не требуется.\n\n"
                f"💡 Чтобы отключить мод: удалите файл pak02_dir.vpk\n"
                f"из папки {lang_folder}\n\n"
                f"⚠️ Напоминание: мод работает ТОЛЬКО при русской озвучке Dota 2."
            )
            QMessageBox.information(self, "✓ Успех!", msg)
        else:
            self.progress_bar.setValue(0)
            self._set_status("Ошибка — смотрите лог", "error")
            QMessageBox.warning(self, "Ошибка", "Обработка завершилась с ошибками. Смотрите лог.")

    def _set_busy(self, busy: bool):
        self.btn_start.setEnabled(not busy)
        self.btn_change_path.setEnabled(not busy)
        self.btn_start.setText("ОБРАБОТКА..." if busy else "ПРИМЕНИТЬ МОД")

    def _on_log_message(self, level: str, msg: str):
        color = LOG_COLORS.get(level, LOG_COLORS["info"])
        prefix = {"warning": "⚠ ", "error": "✗ ", "success": "✓ "}.get(level, "")
        self.log_view.append(
            f'<span style="color: {color};">{prefix}{html.escape(msg)}</span>'
        )
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
