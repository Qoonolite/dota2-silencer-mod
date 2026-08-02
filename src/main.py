import sys
from pathlib import Path

src_path = Path(__file__).parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from app import App
from ui.styles import DARK_THEME


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Dota 2 Sound Silencer")
    app.setApplicationVersion("1.0")
    app.setStyleSheet(DARK_THEME)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()