"""Рендерит главное окно оффскрин и сохраняет скриншот: tools/ui_preview.png."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app import App
from ui.styles import DARK_THEME


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    window = App()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    window.show()
    app.processEvents()

    out = Path(__file__).parent / "ui_preview.png"
    window.grab().save(str(out), "PNG")
    print(f"OK: {out}")


if __name__ == "__main__":
    main()
