from typing import Dict, List, Optional

from gui.styles import apply_button_style, get_minimal_style
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from .file_selection_widget import FileSelectionWidget
from .text_areas_widget import TextAreasWidget


class AnalyzeOutputTabWidget(QWidget):
    file_selected = Signal(list)
    folder_selected = Signal(str)
    preview_requested = Signal(str)
    selection_cleared = Signal()
    input_text_changed = Signal()
    format_settings_clicked = Signal()
    analyze_clicked = Signal()
    download_clicked = Signal()
    clear_clicked = Signal()
    processing_status_changed = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setStyleSheet(get_minimal_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(5)

        file_section_container = QWidget()
        file_section_layout = QVBoxLayout(file_section_container)
        file_section_layout.setContentsMargins(0, 15, 0, 0)
        file_section_layout.setSpacing(0)
        self.file_selection_widget = FileSelectionWidget()
        file_section_layout.addWidget(self.file_selection_widget)

        layout.addWidget(file_section_container)
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(8)
        layout.addWidget(spacer_widget)

        self.text_areas_widget = TextAreasWidget()
        layout.addWidget(self.text_areas_widget, 1)

        button_section = QWidget()
        button_layout = QHBoxLayout(button_section)
        button_layout.setContentsMargins(0, 5, 0, 10)
        button_layout.setSpacing(5)
        button_layout.addStretch()

        self.download_button = QPushButton("ダウンロード")
        apply_button_style(self.download_button, "secondary")
        self.download_button.setFixedWidth(90)
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.download_clicked.emit)
        button_layout.addWidget(self.download_button)

        self.clear_button = QPushButton("内容クリア")
        apply_button_style(self.clear_button, "secondary")
        self.clear_button.setFixedWidth(80)
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear_clicked.emit)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(button_section)

    def _connect_signals(self):
        self.file_selection_widget.file_selected.connect(self.file_selected.emit)
        self.file_selection_widget.folder_selected.connect(self.folder_selected.emit)

        self.file_selection_widget.preview_requested.connect(
            self.preview_requested.emit
        )
        self.file_selection_widget.selection_cleared.connect(
            self.selection_cleared.emit
        )

        self.text_areas_widget.input_text_changed.connect(self.input_text_changed.emit)
        self.text_areas_widget.format_settings_clicked.connect(
            self.format_settings_clicked.emit
        )
        self.text_areas_widget.analyze_clicked.connect(self.analyze_clicked.emit)

        self.processing_status_changed.connect(self.update_processing_status)

    def hide_loading_message(self):
        pass

    def set_input_text(self, text):
        self.text_areas_widget.set_input_text(text)

    def get_input_text(self):
        return self.text_areas_widget.get_input_text()

    def set_format_text(self, text: str):
        self.text_areas_widget.set_format_text(text)

    def set_format_text_with_tag_info(
        self,
        text: str,
        final_adjusted_tags: Optional[List[Dict]] = None,
    ):

        self.text_areas_widget.set_format_text_with_tag_info(
            text, detected_special_tags=final_adjusted_tags
        )

    def append_format_text(self, text: str):
        self.text_areas_widget.append_format_text(text)

    def set_output_text(self, text):
        self.text_areas_widget.set_output_text(text)

    def set_input_stats(self, text):
        self.text_areas_widget.set_input_stats(text)

    def set_format_stats(self, text):
        self.text_areas_widget.set_format_stats(text)

    def set_output_stats(self, text):
        self.text_areas_widget.set_output_stats(text)

    def set_format_settings_button_enabled(self, enabled):
        self.text_areas_widget.set_format_settings_button_enabled(enabled)

    def set_analyze_button_enabled(self, enabled):
        self.text_areas_widget.set_analyze_button_enabled(enabled)

    def set_download_button_enabled(self, enabled):
        self.download_button.setEnabled(enabled)

    def set_clear_button_enabled(self, enabled):
        self.clear_button.setEnabled(enabled)

    def clear_all_content_display(self):
        self.text_areas_widget.clear_all_texts()

        self.file_selection_widget.input_entry.clear()
        self.file_selection_widget.selected_folder = None
        self.file_selection_widget.batch_files = []
        self.file_selection_widget.is_batch_processing = False

        self.set_analyze_button_enabled(False)
        self.set_download_button_enabled(False)
        self.set_format_settings_button_enabled(False)
        self.set_clear_button_enabled(False)
        self.update_processing_status(False, "")

        if hasattr(self.text_areas_widget, "format_stats_label"):
            self.text_areas_widget.format_stats_label.setText("")
            self.text_areas_widget.format_stats_label.setVisible(False)

    def get_selected_files(self):
        return self.file_selection_widget.get_selected_files()

    def get_selected_folder(self):
        return self.file_selection_widget.get_selected_folder()

    def is_batch(self):
        return self.file_selection_widget.is_batch()

    def set_input_path_display(self, text):
        self.file_selection_widget.set_input_path_display(text)

    def get_input_path_display(self):
        text = self.file_selection_widget.get_input_path_display()
        return text

    def update_processing_status(self, is_processing: bool, message: str = ""):
        self.text_areas_widget.update_processing_status(is_processing, message)

        if is_processing:
            self.set_analyze_button_enabled(False)
        else:
            if self.get_input_text().strip():
                self.set_analyze_button_enabled(True)
