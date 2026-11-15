from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow
from ui.main_window import MainWindow


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_window = MainWindow()
        self.setCentralWidget(self.main_window)
        self.setWindowTitle("Dota 2 Sound Silencer")
        icon_path = Path(__file__).parent / "assets" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setMinimumSize(720, 600)
        self.resize(760, 680)
