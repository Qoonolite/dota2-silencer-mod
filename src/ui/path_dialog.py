from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QFileDialog, QMessageBox)
from core.path_finder import PathFinder


class PathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Укажите путь к Dota 2")
        self.resize(550, 180)
        self.selected_path: Path = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        hint = QLabel(
            "Автоматически найти Dota 2 не удалось.\n"
            "Укажите путь к папке 'dota 2 beta' вручную."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)
        
        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(r"C:\Steam\steamapps\common\dota 2 beta")
        self.path_input.setMinimumHeight(40)
        
        btn_browse = QPushButton("Обзор...")
        btn_browse.clicked.connect(self._on_browse)
        btn_browse.setMinimumWidth(100)
        
        path_row.addWidget(self.path_input, stretch=1)
        path_row.addWidget(btn_browse)
        layout.addLayout(path_row)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self._on_ok)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)
    
    def _on_browse(self):
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку 'dota 2 beta'",
            str(Path.home())
        )
        if path:
            self.path_input.setText(path)
    
    def _on_ok(self):
        path = Path(self.path_input.text())
        if not PathFinder.validate_user_path(path):
            QMessageBox.warning(
                self, "Неверный путь",
                "В выбранной папке не найден файл 'game/dota/pak01_dir.vpk'.\n"
                "Убедитесь, что вы выбрали папку 'dota 2 beta'."
            )
            return
        
        self.selected_path = path
        self.accept()