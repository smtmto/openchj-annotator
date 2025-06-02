from gui.styles import (apply_frame_style, apply_scroll_area_style,
                        apply_scroll_content_style)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from .dictionary_settings_widget import DictionarySettingsWidget
from .output_settings import OutputSettingsFrame
from .subcorpus_settings_widget import SubcorpusSettingsWidget


class SettingsTabWidget(QWidget):
    dictionary_settings_changed = Signal()
    show_user_dict_help_requested = Signal()
    open_download_page_requested = Signal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        apply_scroll_area_style(scroll_area)

        scroll_content = QWidget()
        apply_scroll_content_style(scroll_content)
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(20, 5, 20, 5)
        content_layout.setSpacing(15)

        self.dict_settings_widget = DictionarySettingsWidget(
            self.config, scroll_content
        )
        content_layout.addWidget(self.dict_settings_widget)

        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        apply_frame_style(separator1, "separator")
        separator1.setFixedHeight(1)
        content_layout.addWidget(separator1)

        self.subcorpus_settings_widget = SubcorpusSettingsWidget(
            scroll_content, self.config
        )
        content_layout.addWidget(self.subcorpus_settings_widget)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        apply_frame_style(separator2, "separator")
        separator2.setFixedHeight(1)
        content_layout.addWidget(separator2)

        self.output_settings_frame = OutputSettingsFrame(scroll_content, self.config)
        content_layout.addWidget(self.output_settings_frame)

        content_layout.addStretch(1)

        scroll_area.setWidget(scroll_content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def _connect_signals(self):
        self.dict_settings_widget.dictionary_settings_changed.connect(
            self.dictionary_settings_changed.emit
        )
        self.dict_settings_widget.show_user_dict_help_requested.connect(
            self.show_user_dict_help_requested.emit
        )
        self.dict_settings_widget.open_download_page_requested.connect(
            self.open_download_page_requested.emit
        )
        self.subcorpus_settings_widget.config_changed.connect(
            self._save_subcorpus_settings
        )

    def _save_subcorpus_settings(self):
        pass

    def update_controls_state(self):
        if hasattr(self.dict_settings_widget, "toggle_controls"):
            self.dict_settings_widget.toggle_controls()
