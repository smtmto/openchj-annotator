from typing import Optional

from gui.styles import apply_frame_style, apply_input_style, apply_label_style
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit,
                               QVBoxLayout, QWidget)

from config import Config


class SubcorpusSettingsWidget(QWidget):
    config_changed = Signal()

    def __init__(self, parent=None, config: Optional[Config] = None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        self._connect_signals()
        self.load_settings()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.frame = QFrame(self)
        apply_frame_style(self.frame)
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(0, 0, 0, 0)
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel("サブコーパス名:")
        apply_label_style(name_label)
        name_label.setFixedWidth(96)
        input_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        placeholder_text = "サブコーパス名を入力（任意）"
        apply_input_style(self.name_input)
        self.name_input.setPlaceholderText(placeholder_text)
        self.name_input.setFixedWidth(260)
        input_layout.addWidget(self.name_input)
        input_layout.addStretch()
        layout.addLayout(input_layout)
        self.main_layout.addWidget(self.frame)

    def _connect_signals(self):
        self.name_input.textChanged.connect(self._on_name_changed)

    def _on_name_changed(self, text):
        if self.config:
            self.config.config["subcorpus_name"] = text
            self.config.save()
            self.config_changed.emit()

    def load_settings(self):
        if self.config:
            subcorpus_name = self.config.config.get("subcorpus_name", "")
            self.name_input.setText(subcorpus_name)
