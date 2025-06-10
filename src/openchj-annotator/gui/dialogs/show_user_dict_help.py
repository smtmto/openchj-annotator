from pathlib import Path

from gui.styles import apply_button_style
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout


def show_user_dict_help_dialog(parent, help_file_path_str: str):
    help_dialog = QDialog(parent)
    help_dialog.setWindowTitle("ユーザー辞書設定方法")
    help_dialog.setMinimumWidth(540)
    help_dialog.setMinimumHeight(735)

    layout = QVBoxLayout(help_dialog)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)

    help_view = QWebEngineView()

    help_file_path = Path(help_file_path_str)
    if help_file_path.exists() and help_file_path.is_file():
        help_view.setUrl(QUrl.fromLocalFile(str(help_file_path.resolve())))
    else:
        error_html = f"<h1>エラー</h1><p>ヘルプファイルが見つかりません:<br>{help_file_path_str}</p>"
        help_view.setHtml(error_html)

    layout.addWidget(help_view)

    close_button = QPushButton("閉じる")
    apply_button_style(close_button, "secondary")
    close_button.clicked.connect(help_dialog.close)

    button_layout = QHBoxLayout()
    button_layout.addStretch()
    button_layout.addWidget(close_button)
    layout.addLayout(button_layout)

    help_dialog.exec()
