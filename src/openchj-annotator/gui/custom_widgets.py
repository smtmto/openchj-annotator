from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QCheckBox


class CustomCheckBox(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        box_size = 13
        box_x = 1
        box_y = (self.height() - box_size) // 2
        box_rect = QRect(box_x, box_y, box_size, box_size)

        if self.isChecked():
            if self.isEnabled():
                painter.fillRect(box_rect, QColor("#0078d7"))
                pen = QPen(QColor("#0078d7"), 1)
            else:
                painter.fillRect(box_rect, QColor("#cccccc"))
                pen = QPen(QColor("#cccccc"), 1)
        else:
            if self.isEnabled():
                painter.fillRect(box_rect, QColor("white"))
                pen = QPen(QColor("#999999"), 1)
            else:
                painter.fillRect(box_rect, QColor("#f0f0f0"))
                pen = QPen(QColor("#cccccc"), 1)

        painter.setPen(pen)
        painter.drawRoundedRect(box_rect, 2, 2)

        if self.isChecked():
            check_color = QColor("white") if self.isEnabled() else QColor("#666666")
            pen = QPen(check_color, 2)
            painter.setPen(pen)
            painter.drawLine(box_x + 3, box_y + 6, box_x + 5, box_y + 9)
            painter.drawLine(box_x + 5, box_y + 9, box_x + 10, box_y + 3)

        text_rect = QRect(box_size + 10, 0, self.width() - box_size - 10, self.height())
        text_color = QColor("#333333") if self.isEnabled() else QColor("#999999")
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignVCenter, self.text())
