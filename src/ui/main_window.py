import json
import traceback
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QLineEdit,
                             QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt
from core.path_finder import PathFinder
from ui.path_dialog import PathDialog
from utils.config import Config
from utils.logger import GUILogger


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.log = GUILogger()
        self.path_finder = PathFinder()
        self.log.message.connect(self._on_log_message)
        self._init_ui()
        self._init_path()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Dota 2 Silencer mod")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff; padding: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        subtitle = QLabel("Отключение надоедливых звуковых фраз колеса чата")
        subtitle.setStyleSheet("font-size: 13px; color: #ffffff; padding-bottom: 3px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        warn_label = QLabel(
            "⚠️ Мод работает только для русской версии игры (текст + озвучка).\n"
            "Для других языков не работает."
        )
        warn_label.setStyleSheet("color: #ffd93d; background-color: #2d2d2d; padding: 6px; border-radius: 4px; font-size: 11px;")
        warn_label.setWordWrap(True)
        main_layout.addWidget(warn_label)

        path_group = QGroupBox("Путь к Dota 2")
        path_group.setStyleSheet("margin-top: 2px;")
        path_layout = QHBoxLayout(path_group)
        path_layout.setSpacing(8)
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Путь не найден — нажмите 'Изменить'")
        self.path_input.setMinimumHeight(30)
        self.btn_change_path = QPushButton("Изменить")
        self.btn_change_path.clicked.connect(self._on_change_path)
        self.btn_change_path.setMinimumWidth(90)
        path_layout.addWidget(self.path_input, stretch=1)
        path_layout.addWidget(self.btn_change_path)
        main_layout.addWidget(path_group)

        self.btn_start = QPushButton("ПРИМЕНИТЬ")
        self.btn_start.setObjectName("primary")
        self.btn_start.setStyleSheet("""
            QPushButton#primary {
                background-color: #4a9eff;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton#primary:hover {
                background-color: #6ab0ff;
            }
            QPushButton#primary:pressed {
                background-color: #2a7edf;
            }
        """)
        self.btn_start.clicked.connect(self._on_start)
        self.btn_start.setMinimumHeight(40)
        main_layout.addWidget(self.btn_start)

        log_group = QGroupBox("Лог обработки")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(6, 12, 6, 6)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(100)
        self.log_view.setStyleSheet("""
            background-color: #1b2838; color: #c7d5e0; border: 1px solid #3d6a8e;
            border-radius: 4px; padding: 4px; font-family: "Consolas", monospace; font-size: 11px;
        """)
        log_layout.addWidget(self.log_view)
        main_layout.addWidget(log_group)

        author_frame = QWidget()
        author_frame.setStyleSheet("""
            background-color: #2a2a3e;
            border: 1px solid #45475a;
            border-radius: 4px;
            padding: 4px;
        """)
        author_layout = QVBoxLayout(author_frame)
        author_layout.setSpacing(1)
        author_layout.setContentsMargins(4, 4, 4, 4)

        author_label = QLabel("Автор: Qoonolite")
        author_label.setStyleSheet("color: #cdd6f4; font-size: 11px;")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_layout.addWidget(author_label)

        profile_link = QLabel('<a href="https://steamcommunity.com/id/Qnlite/" style="color: #89b4fa;">Профиль Steam</a>')
        profile_link.setOpenExternalLinks(True)
        profile_link.setStyleSheet("font-size: 11px;")
        profile_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_layout.addWidget(profile_link)

        donate_link = QLabel(
            'Поддержать: '
            '<a href="https://www.donationalerts.com/r/qoonolite" style="color: #f9e2af; font-size: 14px; font-weight: bold;">'
            'DONATE</a>'
        )
        donate_link.setOpenExternalLinks(True)
        donate_link.setStyleSheet("font-size: 11px;")
        donate_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_layout.addWidget(donate_link)

        main_layout.addWidget(author_frame)

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
        self.btn_start.setEnabled(False)
        self.btn_start.setText("ОБРАБОТКА...")

        try:
            from core.processor import SoundProcessor
            processor = SoundProcessor(Path(dota_path), "russian", self.log)
            success = processor.process_categories(["wheel_sounds"], {
                "wheel_sounds": [
                    "sounds/talentcontent/**/*.vsnd_c",
                    "sounds/teamfancontent/**/*.vsnd_c"
                ]
            })

            if success:
                lang_folder = Path(dota_path) / "game" / "dota_russian"
                msg = (
                    f"✅ Обработка успешно завершена!\n\n"
                    f"📁 Создан архив: {lang_folder}\\pak02_dir.vpk\n\n"
                    f"Звуковые фразы колеса чата отключены для русской версии игры.\n"
                    f"Никаких дополнительных параметров запуска не требуется.\n\n"
                    f"💡 Чтобы отключить мод: удалите файл pak02_dir.vpk\n"
                    f"из папки {lang_folder}\n\n"
                    f"⚠️ Напоминание: мод работает ТОЛЬКО для русской версии Dota 2."
                )
                QMessageBox.information(self, "✓ Успех!", msg)
            else:
                QMessageBox.warning(self, "Ошибка", "Обработка завершилась с ошибками. Смотрите лог.")

        except Exception as e:
            error_details = traceback.format_exc()
            self.log.error(f"Критическая ошибка: {e}")
            self.log.error(error_details)
            QMessageBox.critical(self, "Критическая ошибка", f"Произошла ошибка:\n\n{str(e)}\n\nДетали в логе.")
        finally:
            self.btn_start.setEnabled(True)
            self.btn_start.setText("ПРИМЕНИТЬ")

    def _on_log_message(self, msg: str):
        self.log_view.append(msg)
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())