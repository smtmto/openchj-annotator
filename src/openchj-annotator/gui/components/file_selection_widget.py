import os

from gui.styles import (apply_button_style, apply_input_style,
                        apply_label_style, apply_message_box_style)
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QSizePolicy, QWidget)


class FileSelectionWidget(QWidget):
    file_selected = Signal(list)
    folder_selected = Signal(str)
    selection_cleared = Signal()
    preview_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = None
        self.batch_files = []
        self.is_batch_processing = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        file_label = QLabel("入力ファイル/フォルダ:")
        apply_label_style(file_label, "default")
        layout.addWidget(file_label)

        self.input_entry = QLineEdit()
        apply_input_style(self.input_entry)
        self.input_entry.setMinimumWidth(200)
        self.input_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_entry.setPlaceholderText("ファイルまたはフォルダを選択してください")
        layout.addWidget(self.input_entry)

        browse_file_button = QPushButton("ファイル選択")
        apply_button_style(browse_file_button, "secondary")
        browse_file_button.setFixedWidth(90)
        browse_file_button.clicked.connect(self.browse_file)
        layout.addWidget(browse_file_button)

        browse_folder_button = QPushButton("フォルダ選択")
        apply_button_style(browse_folder_button, "secondary")
        browse_folder_button.setFixedWidth(90)
        browse_folder_button.clicked.connect(self.browse_folder)
        layout.addWidget(browse_folder_button)

    def browse_file(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "ファイルを選択",
            "",
            "テキストファイル (*.txt);;すべてのファイル (*.*)",
        )

        if filenames:
            if len(filenames) > 50:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("ファイル数制限エラー")
                msg_box.setText(
                    f"選択されたファイル数: {len(filenames)}件\n\n"
                    "一度に処理できるファイルは50件までです。"
                )
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec_()
                return

            try:
                total_size = sum(os.path.getsize(f) for f in filenames)
                if total_size > 10 * 1024 * 1024:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("ファイルサイズ制限エラー")
                    msg_box.setText(
                        f"選択されたファイルの合計サイズ: {total_size / 1024 / 1024:.1f}MB\n\n"
                        "一度に処理できるファイルの合計サイズは10MBまでです。"
                    )
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    self._style_message_box_buttons(msg_box)
                    msg_box.exec_()
                    return
            except OSError as e:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("エラー")
                msg_box.setText(f"ファイルサイズの取得中にエラーが発生しました: {e}")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec_()
                return

            self.batch_files = filenames
            self.selected_folder = None

            if len(filenames) == 1:
                self.input_entry.setText(filenames[0])
                self.is_batch_processing = False
                self.file_selected.emit(filenames)
                self.preview_requested.emit(filenames[0])
            else:
                self.input_entry.setText(filenames[0])
                self.is_batch_processing = True
                self.file_selected.emit(filenames)
                if filenames:
                    self.preview_requested.emit(filenames[0])

    def browse_folder(self):

        from PySide6.QtCore import QTimer

        folder = QFileDialog.getExistingDirectory(self, "フォルダを選択")
        if folder:
            QTimer.singleShot(0, lambda: self._complete_folder_selection(folder))

    def _complete_folder_selection(self, folder):
        self.input_entry.setText(folder)
        self.input_entry.repaint()
        self.selected_folder = folder
        self.batch_files = []
        self.is_batch_processing = True
        self.folder_selected.emit(folder)

    def get_selected_files(self):
        return self.batch_files

    def get_selected_folder(self):
        return self.selected_folder

    def is_batch(self):
        return self.is_batch_processing

    def clear_selection(self):
        self.input_entry.clear()
        self.selected_folder = None
        self.batch_files = []
        self.is_batch_processing = False
        self.selection_cleared.emit()

    def set_input_path_display(self, text):
        self.input_entry.setText(text)
        self.input_entry.repaint()

    def get_input_path_display(self):
        text = self.input_entry.text()
        return text

    def _style_message_box_buttons(self, msg_box):
        apply_message_box_style(msg_box)
