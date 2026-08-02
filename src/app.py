from PyQt6.QtWidgets import QMainWindow
from ui.main_window import MainWindow


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_window = MainWindow()
        self.setCentralWidget(self.main_window)
        self.setWindowTitle("Dota 2 Sound Silencer")
        self.setFixedSize(700, 520)