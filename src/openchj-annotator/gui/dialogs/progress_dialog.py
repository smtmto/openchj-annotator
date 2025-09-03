from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QSizePolicy, QVBoxLayout


class ProgressDialog(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("処理中...")

        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)

        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.label)
        self.setLayout(layout)

    def start_animation(self, base_text="処理中..."):
        self.set_message(base_text)

    def stop_animation(self):
        pass

    def set_message(self, message):
        self.label.setText(message)
        QApplication.processEvents()

    def close(self):
        super().close()

    def close_event(self, event):
        super().close_event(event)
