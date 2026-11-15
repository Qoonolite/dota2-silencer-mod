"""Генерирует иконку приложения: src/assets/app_icon.png и app_icon.ico."""
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (QPixmap, QPainter, QLinearGradient, QColor,
                         QPen, QPolygonF)
from PyQt6.QtWidgets import QApplication

SIZE = 256
OUT_DIR = Path(__file__).parent.parent / "src" / "assets"


def render(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)

    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    s = size / 256  # масштаб относительно базового размера

    # Фон: скруглённый квадрат с градиентом в цветах темы
    grad = QLinearGradient(0, 0, 0, size)
    grad.setColorAt(0, QColor("#2a475e"))
    grad.setColorAt(1, QColor("#171d25"))
    p.setBrush(grad)
    p.setPen(QPen(QColor("#3d6a8e"), max(2, int(6 * s))))
    p.drawRoundedRect(QRectF(8 * s, 8 * s, 240 * s, 240 * s), 52 * s, 52 * s)

    # Динамик
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#c7d5e0"))
    p.drawRoundedRect(QRectF(56 * s, 104 * s, 32 * s, 48 * s), 5 * s, 5 * s)
    p.drawPolygon(QPolygonF([
        QPointF(84 * s, 106 * s),
        QPointF(134 * s, 74 * s),
        QPointF(134 * s, 182 * s),
        QPointF(84 * s, 150 * s),
    ]))

    # Звуковые дуги
    arc_pen = QPen(QColor("#66c0f4"), max(2, int(11 * s)))
    arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(arc_pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(122 * s, 92 * s, 48 * s, 72 * s), -50 * 16, 100 * 16)
    p.drawArc(QRectF(112 * s, 72 * s, 88 * s, 112 * s), -45 * 16, 90 * 16)

    # Перечёркивающая линия
    slash_pen = QPen(QColor("#e74c3c"), max(2, int(17 * s)))
    slash_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(slash_pen)
    p.drawLine(QPointF(70 * s, 66 * s), QPointF(196 * s, 192 * s))

    p.end()
    return pm


def main():
    app = QApplication(sys.argv)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pixmap = render(SIZE)
    png_path = OUT_DIR / "app_icon.png"
    ico_path = OUT_DIR / "app_icon.ico"
    pixmap.save(str(png_path), "PNG")
    pixmap.save(str(ico_path), "ICO")
    print(f"OK: {png_path}")
    print(f"OK: {ico_path}")


if __name__ == "__main__":
    main()
