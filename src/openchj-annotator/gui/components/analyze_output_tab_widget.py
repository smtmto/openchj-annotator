from typing import Dict, List, Optional

from gui.styles import DEFAULT_FONT_FAMILY, apply_button_style, get_minimal_style
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

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
    output_format_changed = Signal(str)

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

        self.output_format_group = QButtonGroup()
        self.openchj_radio = QRadioButton("OpenCHJ形式")
        self.simple_radio = QRadioButton("書字形出現形+語彙素+品詞")

        self.openchj_radio.setChecked(True)
        self.output_format_group.addButton(self.openchj_radio, 0)
        self.output_format_group.addButton(self.simple_radio, 1)

        self.output_format_group.buttonToggled.connect(self._on_output_format_changed)

        radio_font = QFont(DEFAULT_FONT_FAMILY, 11)
        self.openchj_radio.setFont(radio_font)
        self.simple_radio.setFont(radio_font)

        button_layout.addSpacing(10)
        button_layout.addWidget(self.openchj_radio)
        button_layout.addWidget(self.simple_radio)
        button_layout.addStretch()

        self.download_button = QPushButton("出力")
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

        try:
            target_h = self.text_areas_widget.analyze_button.sizeHint().height()
            self.file_selection_widget.browse_file_button.setFixedHeight(target_h)
            self.file_selection_widget.browse_folder_button.setFixedHeight(target_h)
            self.download_button.setFixedHeight(target_h)
            self.clear_button.setFixedHeight(target_h)
        except Exception:
            pass

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
        self.text_areas_widget.input_text_changed.connect(self._on_input_text_changed)
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

    def set_output_text(self, text, format_type=None):
        if format_type is None:
            format_type = self.get_output_format()
        self.text_areas_widget.set_output_text(text, format_type)

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

    def _on_input_text_changed(self):
        input_text = self.get_input_text()
        self.file_selection_widget.update_button_states(input_text)

        has_file_or_folder = self.file_selection_widget.has_file_or_folder_selected()
        has_manual_text = bool(input_text.strip()) and not has_file_or_folder

        if has_manual_text:
            self.set_format_settings_button_enabled(True)

        self.text_areas_widget.set_input_text_readonly(has_file_or_folder)

    def _on_output_format_changed(self, button, checked):
        if checked:
            if button == self.openchj_radio:
                self.output_format_changed.emit("openchj")
            elif button == self.simple_radio:
                self.output_format_changed.emit("simple")

    def get_output_format(self):
        if self.openchj_radio.isChecked():
            return "openchj"
        elif self.simple_radio.isChecked():
            return "simple"
        return "openchj"
