from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar, 
                             QTextEdit, QPushButton)
from PyQt6.QtCore import Qt


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обработка звуков")
        self.resize(500, 300)
        self.setModal(True)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        self.lbl_status = QLabel("Подготовка...")
        layout.addWidget(self.lbl_status)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)
        
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.setEnabled(False)
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)
    
    def set_status(self, text: str):
        self.lbl_status.setText(text)
    
    def set_progress(self, value: int):
        self.progress.setValue(value)
    
    def append_log(self, text: str):
        self.log_view.append(text)
    
    def finish(self, success: bool, message: str):
        self.btn_close.setEnabled(True)
        self.set_status(message)
        self.append_log(f"\n{'✓' if success else '✗'} {message}")