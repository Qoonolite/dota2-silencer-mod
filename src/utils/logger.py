import logging
import os
import sys
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class GUILogger(QObject):
    # Сигнал: (уровень, текст). Уровни: info, warning, error, success, progress
    message = pyqtSignal(str, str)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', Path.home()))
        else:
            base = Path.home()
        
        log_dir = base / "DotaSoundSilencer" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "app.log"
        
        self.logger = logging.getLogger("DotaSoundSilencer")
        self.logger.setLevel(logging.DEBUG)
        
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(fh)
    
    def info(self, msg: str):
        self.logger.info(msg)
        self.message.emit("info", msg)

    def warning(self, msg: str):
        self.logger.warning(msg)
        self.message.emit("warning", msg)

    def error(self, msg: str):
        self.logger.error(msg)
        self.message.emit("error", msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def success(self, msg: str):
        self.logger.info(msg)
        self.message.emit("success", msg)

    def progress(self, msg: str):
        self.logger.info(msg)
        self.message.emit("progress", msg)