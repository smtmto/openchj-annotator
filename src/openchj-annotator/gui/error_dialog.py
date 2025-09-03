import sys

from PySide6.QtWidgets import QApplication, QMessageBox


def show_error_and_exit(title, message):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)
    error_box.setWindowTitle(title)
    error_box.setText(message)
    error_box.setStandardButtons(QMessageBox.Ok)
    error_box.exec()

    sys.exit(1)
