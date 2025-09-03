import os

from gui.styles import (
    apply_button_style,
    apply_input_style,
    apply_label_style,
    apply_message_box_style,
)
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QWidget,
)


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
        self.input_entry.setReadOnly(False)
        self.input_entry.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input_entry)

        self.browse_file_button = QPushButton("ファイル選択")
        apply_button_style(self.browse_file_button, "secondary")
        self.browse_file_button.setFixedWidth(90)
        self.browse_file_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_file_button)

        self.browse_folder_button = QPushButton("フォルダ選択")
        apply_button_style(self.browse_folder_button, "secondary")
        self.browse_folder_button.setFixedWidth(90)
        self.browse_folder_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_folder_button)

    def browse_file(self):
        if self.input_entry.text().strip():
            return

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
        if self.input_entry.text().strip():
            return

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

    def _on_text_changed(self):
        self.update_button_states()

    def update_button_states(self, external_text=""):
        file_path_text = self.input_entry.text().strip()
        has_any_text = bool(file_path_text) or bool(external_text.strip())

        self.browse_file_button.setEnabled(not has_any_text)
        self.browse_folder_button.setEnabled(not has_any_text)

        if has_any_text:
            from gui.styles import apply_button_style

            apply_button_style(self.browse_file_button, "disabled")
            apply_button_style(self.browse_folder_button, "disabled")
        else:
            from gui.styles import apply_button_style

            apply_button_style(self.browse_file_button, "secondary")
            apply_button_style(self.browse_folder_button, "secondary")

    def has_file_or_folder_selected(self):
        return bool(self.selected_folder) or bool(self.batch_files)
