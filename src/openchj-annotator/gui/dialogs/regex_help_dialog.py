import logging
from pathlib import Path

from gui.styles import TEXT_AREA_STYLE
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QMessageBox, QPushButton,
                               QTextEdit, QVBoxLayout)


class TextHelpDialog(QDialog):
    def __init__(self, html_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("正規表現の使い方")
        self.setMinimumSize(560, 600)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_edit.setStyleSheet(TEXT_AREA_STYLE["stylesheet"])
        layout.addWidget(self.text_edit)

        try:
            self._load_html(html_path)
        except Exception as e:
            logging.error(f"Error loading help file: {e}")
            QMessageBox.critical(self, "エラー", f"ヘルプファイルの読み込みに失敗しました:\n{e}")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def _load_html(self, html_path):
        path_obj = Path(html_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {html_path}")
        with open(path_obj, "r", encoding="utf-8") as f:
            html_content = f.read()
        self.text_edit.setHtml(html_content)


def show_regex_help_dialog(parent, html_path):
    try:
        dialog = TextHelpDialog(html_path, parent)
        return dialog.exec()
    except Exception as e:
        logging.error(f"Error showing help dialog: {e}")
        QMessageBox.critical(parent, "エラー", f"ヘルプの表示に失敗しました:\n{e}")
        return False
