import html
import traceback
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.categories import CATEGORIES, HERO_FULL_CONFIG_KEY
from core.path_finder import PathFinder
from core.processor import SoundProcessor
from ui.path_dialog import PathDialog
from utils.config import Config
from utils.logger import GUILogger


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
    progress_changed = pyqtSignal(int, int)
    finished_ok = pyqtSignal(bool)

    def __init__(self, dota_path: str, categories: List[str], hero_full: bool, parent=None):
        super().__init__(parent)
        self.dota_path = dota_path
        self.categories = categories
        self.hero_full = hero_full

    def run(self):
        log = GUILogger()
        try:
            processor = SoundProcessor(Path(self.dota_path), "russian", log)
            ok = processor.process_categories(
                self.categories,
                on_progress=lambda current, total: self.progress_changed.emit(current, total),
                hero_full=self.hero_full,
            )
        except Exception as exc:
            log.error(f"Критическая ошибка: {exc}")
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
        self.category_checks = {}
        self.log.message.connect(self._on_log_message)
        self._init_ui()
        self._init_path()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 16, 20, 14)

        header = QHBoxLayout()
        header.setSpacing(14)
        icon_label = QLabel()
        icon_path = _assets_dir() / "app_icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(
                48, 48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(48, 48)
        header.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Dota 2 Silencer")
        title.setObjectName("title")
        subtitle = QLabel("Отключение звуков колеса чата, насмешек и граффити")
        subtitle.setObjectName("subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col, stretch=1)

        version = QLabel("v2.2")
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

        categories_group = QGroupBox("Что отключить")
        self._add_shadow(categories_group)
        categories_layout = QVBoxLayout(categories_group)
        categories_layout.setContentsMargins(12, 14, 12, 12)
        categories_layout.setSpacing(8)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)
        self.btn_select_all = QPushButton("Выбрать все")
        self.btn_select_all.setObjectName("compactButton")
        self.btn_select_all.clicked.connect(lambda: self._set_all_categories(True))
        self.btn_select_none = QPushButton("Снять все")
        self.btn_select_none.setObjectName("compactButton")
        self.btn_select_none.clicked.connect(lambda: self._set_all_categories(False))
        self.selection_counter = QLabel()
        self.selection_counter.setObjectName("subtitle")
        controls_row.addWidget(self.btn_select_all)
        controls_row.addWidget(self.btn_select_none)
        controls_row.addStretch()
        controls_row.addWidget(self.selection_counter)
        categories_layout.addLayout(controls_row)

        self.categories_scroll = QScrollArea()
        self.categories_scroll.setObjectName("categoriesScroll")
        self.categories_scroll.setWidgetResizable(True)
        self.categories_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.categories_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.categories_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.categories_scroll.setMinimumHeight(250)
        self.categories_scroll.viewport().setAutoFillBackground(False)

        categories_content = QWidget()
        categories_content.setObjectName("categoriesContent")
        categories_content.setAutoFillBackground(False)
        grid = QGridLayout(categories_content)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.hero_full_check = None
        for index, (cat_id, category) in enumerate(CATEGORIES.items()):
            card = QWidget()
            card.setObjectName("categoryCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 8, 6)
            card_layout.setSpacing(0)

            check = QCheckBox(category.label)
            check.setObjectName("categoryCheck")
            check.setChecked(bool(self.config.get(f"cat_{cat_id}", category.default)))
            tooltip = category.tooltip
            if category.warning:
                tooltip = f"{tooltip}\n\nВнимание: {category.warning}"
            check.setToolTip(tooltip)
            check.toggled.connect(
                lambda state, category_id=cat_id: self._on_category_toggled(category_id, state)
            )
            self.category_checks[cat_id] = check
            card_layout.addWidget(check)

            description = QLabel(category.description)
            description.setObjectName("categoryDescription")
            description.setWordWrap(True)
            description.setContentsMargins(28, 0, 0, 0)
            description.setToolTip(tooltip)
            card_layout.addWidget(description)

            if category.safe_file_pattern:
                full_row = QHBoxLayout()
                full_row.setContentsMargins(28, 0, 0, 0)
                full_row.setSpacing(6)
                self.hero_full_check = QCheckBox("Отключить всё, включая обычные реплики")
                self.hero_full_check.setObjectName("heroFullCheck")
                self.hero_full_check.setChecked(bool(self.config.get(HERO_FULL_CONFIG_KEY, False)))
                self.hero_full_check.setToolTip(category.warning)
                self.hero_full_check.toggled.connect(self._on_hero_full_toggled)
                full_row.addWidget(self.hero_full_check)
                warning_icon = QLabel("⚠")
                warning_icon.setObjectName("warningIcon")
                warning_icon.setToolTip(category.warning)
                full_row.addWidget(warning_icon)
                full_row.addStretch()
                card_layout.addLayout(full_row)

            grid.addWidget(card, index // 2, index % 2)

        self.categories_scroll.setWidget(categories_content)
        categories_layout.addWidget(self.categories_scroll)
        main_layout.addWidget(categories_group, stretch=1)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        self.btn_start = QPushButton("ПРИМЕНИТЬ МОД")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self._on_start)
        self.btn_start.setMinimumHeight(48)
        self.btn_restore = QPushButton("Восстановить всё")
        self.btn_restore.clicked.connect(self._on_restore)
        self.btn_restore.setMinimumHeight(48)
        actions_row.addWidget(self.btn_start, stretch=2)
        actions_row.addWidget(self.btn_restore, stretch=1)
        main_layout.addLayout(actions_row)

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

        self.btn_toggle_log = QPushButton("Показать журнал")
        self.btn_toggle_log.setObjectName("compactButton")
        self.btn_toggle_log.clicked.connect(self._toggle_log)
        main_layout.addWidget(self.btn_toggle_log)

        self.log_group = QGroupBox("Журнал")
        log_layout = QVBoxLayout(self.log_group)
        log_layout.setContentsMargins(8, 14, 8, 8)
        self.log_view = QTextEdit()
        self.log_view.setObjectName("logView")
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(120)
        log_layout.addWidget(self.log_view)
        self.log_group.setVisible(False)
        main_layout.addWidget(self.log_group)

        author_frame = QWidget()
        author_frame.setObjectName("authorCard")
        author_layout = QHBoxLayout(author_frame)
        author_layout.setContentsMargins(12, 8, 12, 8)
        author_layout.setSpacing(16)
        author_label = QLabel("Автор: Qoonolite")
        author_label.setObjectName("authorName")
        author_layout.addWidget(author_label)
        author_layout.addStretch()
        profile_link = QLabel(
            '<a href="https://steamcommunity.com/id/Qnlite/" '
            'style="color: #a8c7fa; text-decoration: none;">Профиль Steam</a>'
        )
        profile_link.setOpenExternalLinks(True)
        author_layout.addWidget(profile_link)
        donate_link = QLabel(
            '<a href="https://www.donationalerts.com/r/qoonolite" '
            'style="color: #fdd663; font-weight: bold; text-decoration: none;">Поддержать ♥</a>'
        )
        donate_link.setOpenExternalLinks(True)
        author_layout.addWidget(donate_link)
        main_layout.addWidget(author_frame)

        self._update_counter()
        self._update_hero_mode()

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 60))
        widget.setGraphicsEffect(shadow)

    def _set_status(self, text: str, state: str = "idle"):
        self.status_label.setText(text)
        self.status_dot.setStyleSheet(f"color: {STATUS_COLORS.get(state, STATUS_COLORS['idle'])};")

    def _on_category_toggled(self, cat_id: str, state: bool):
        self.config.set(f"cat_{cat_id}", bool(state))
        self._update_counter()
        if cat_id == "hero_chat":
            self._update_hero_mode()

    def _on_hero_full_toggled(self, state: bool):
        self.config.set(HERO_FULL_CONFIG_KEY, bool(state))

    def _update_counter(self):
        selected = sum(check.isChecked() for check in self.category_checks.values())
        self.selection_counter.setText(f"Выбрано: {selected} из {len(CATEGORIES)}")

    def _update_hero_mode(self):
        if self.hero_full_check:
            enabled = self.category_checks["hero_chat"].isChecked() and self.btn_start.isEnabled()
            self.hero_full_check.setEnabled(enabled)

    def _set_all_categories(self, checked: bool):
        for check in self.category_checks.values():
            check.setChecked(checked)
        self._update_counter()
        self._update_hero_mode()

    def _toggle_log(self):
        visible = not self.log_group.isVisible()
        self.log_group.setVisible(visible)
        self.btn_toggle_log.setText("Скрыть журнал" if visible else "Показать журнал")

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

        selected = [cat_id for cat_id, check in self.category_checks.items() if check.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одну категорию для отключения.")
            return

        hero_full = bool(
            self.hero_full_check
            and self.hero_full_check.isChecked()
            and self.category_checks["hero_chat"].isChecked()
        )
        self.log_view.clear()
        self._set_busy(True)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self._set_status("Поиск файлов в архиве...", "busy")

        self._worker = ProcessWorker(dota_path, selected, hero_full, self)
        self._worker.progress_changed.connect(self._on_progress)
        self._worker.finished_ok.connect(lambda ok: self._on_finished(ok, dota_path))
        self._worker.finished.connect(self._worker.deleteLater)
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
                f"Обработка успешно завершена.\n\n"
                f"Создан архив: {lang_folder}\\pak02_dir.vpk\n\n"
                f"Выбранные категории отключены для русской версии игры.\n"
                f"Никаких дополнительных параметров запуска не требуется.\n\n"
                f"Чтобы отключить мод, нажмите «Восстановить всё» или удалите pak02_dir.vpk.\n\n"
                f"Напоминание: мод работает только при русской озвучке Dota 2."
            )
            QMessageBox.information(self, "Успех", msg)
        else:
            self.progress_bar.setValue(0)
            self._set_status("Ошибка — откройте журнал", "error")
            QMessageBox.warning(self, "Ошибка", "Обработка завершилась с ошибками. Смотрите журнал.")

    def _on_restore(self):
        dota_path = self.path_input.text()
        if not dota_path or not PathFinder.validate_user_path(Path(dota_path)):
            QMessageBox.warning(self, "Ошибка", "Укажите корректный путь к Dota 2")
            return
        output_vpk = SoundProcessor.output_path(Path(dota_path))
        if not output_vpk.exists():
            QMessageBox.information(self, "Восстановление", "Архив мода не найден. Игра уже использует исходные файлы.")
            return

        answer = QMessageBox.question(
            self,
            "Восстановить всё",
            "Удалить созданный pak02_dir.vpk и восстановить исходные звуки и граффити?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            SoundProcessor.restore(Path(dota_path), "russian", self.log)
        except OSError as exc:
            self.log.error(f"Не удалось удалить архив: {exc}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить архив:\n{exc}")
            return
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self._set_status("Исходные файлы восстановлены", "ok")
        QMessageBox.information(self, "Восстановление", "Мод удалён. Перезапустите Dota 2.")

    def _set_busy(self, busy: bool):
        self.btn_start.setEnabled(not busy)
        self.btn_restore.setEnabled(not busy)
        self.btn_change_path.setEnabled(not busy)
        self.btn_select_all.setEnabled(not busy)
        self.btn_select_none.setEnabled(not busy)
        for check in self.category_checks.values():
            check.setEnabled(not busy)
        self.btn_start.setText("ОБРАБОТКА..." if busy else "ПРИМЕНИТЬ МОД")
        self._update_hero_mode()

    def _on_log_message(self, level: str, msg: str):
        color = LOG_COLORS.get(level, LOG_COLORS["info"])
        prefix = {"warning": "⚠ ", "error": "✗ ", "success": "✓ "}.get(level, "")
        self.log_view.append(
            f'<span style="color: {color};">{prefix}{html.escape(msg)}</span>'
        )
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
