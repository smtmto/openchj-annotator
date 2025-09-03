import logging
from typing import Optional

from gui.styles import apply_button_style, apply_dialog_style
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

from config import Config

from .aozora_settings_widget import AozoraSettingsWidget
from .regex_settings_widget import RegexSettingsWidget
from .settings_model import SettingsModel
from .tag_settings_widget import TagSettingsWidget
from .whitespace_settings_widget import WhitespaceSettingsWidget


class FormatSettingsDialog(QDialog):
    settings_applied = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config: Optional[Config] = None
        if parent and hasattr(parent, "config") and isinstance(parent.config, Config):
            self.config = parent.config
        else:
            logging.warning(
                "FormatSettingsDialog: parent.config is not a Config object."
            )

        self.settings_model = SettingsModel(self.config)
        self.setWindowTitle("整形設定")
        self.setMinimumWidth(540)
        apply_dialog_style(self)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        self.tag_settings_widget = TagSettingsWidget(self, self.config)
        self.whitespace_settings_widget = WhitespaceSettingsWidget(self, self.config)
        self.aozora_settings_widget = AozoraSettingsWidget(self, self.config)
        self.regex_settings_widget = RegexSettingsWidget(self, self.config)

        layout.addWidget(self.tag_settings_widget)
        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.whitespace_settings_widget)
        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.aozora_settings_widget)
        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.regex_settings_widget)

        button_layout = QHBoxLayout()
        self.clear_dialog_button = QPushButton("設定クリア")
        apply_button_style(self.clear_dialog_button, "secondary")
        self.clear_dialog_button.setFocusPolicy(Qt.NoFocus)
        button_layout.addWidget(self.clear_dialog_button)
        button_layout.addStretch()

        self.apply_button = QPushButton("整形テキストに反映")
        apply_button_style(self.apply_button, "secondary")
        self.apply_button.setFocusPolicy(Qt.NoFocus)
        button_layout.addWidget(self.apply_button)

        self.close_button = QPushButton("閉じる")
        apply_button_style(self.close_button, "secondary")
        self.close_button.setFocusPolicy(Qt.NoFocus)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _connect_signals(self):
        self.tag_settings_widget.config_changed.connect(self._on_settings_changed)
        self.whitespace_settings_widget.config_changed.connect(
            self._on_settings_changed
        )
        self.aozora_settings_widget.config_changed.connect(self._on_settings_changed)
        self.regex_settings_widget.config_changed.connect(self._on_settings_changed)

        self.clear_dialog_button.clicked.connect(self._clear_dialog_settings)
        self.apply_button.clicked.connect(self._apply_settings)
        self.close_button.clicked.connect(self.reject)

    def _on_settings_changed(self):
        pass

    def _clear_dialog_settings(self):
        self.tag_settings_widget.clear_settings()
        self.whitespace_settings_widget.clear_settings()
        self.aozora_settings_widget.clear_settings()
        self.regex_settings_widget.clear_settings()

    def _apply_settings(self):
        tag_settings = self.tag_settings_widget.get_current_settings()
        whitespace_settings = self.whitespace_settings_widget.get_current_settings()
        aozora_settings = self.aozora_settings_widget.get_current_settings()
        regex_settings = self.regex_settings_widget.get_current_settings()

        preview_settings = {}
        preview_settings.update(tag_settings)
        preview_settings.update(whitespace_settings)
        preview_settings.update(aozora_settings)
        preview_settings.update(regex_settings)

        formatted_settings = {
            "remove_tags": {
                "enabled": preview_settings.get("tag_settings", {}).get(
                    "enabled", False
                ),
                "types": preview_settings.get("tag_settings", {}).get("types", []),
                "mode": preview_settings.get("tag_settings", {}).get(
                    "mode", "remove_with_content"
                ),
            },
            "aozora_cleanup": preview_settings.get("aozora_cleanup", False),
            "regex_settings": {
                "enabled": preview_settings.get("regex_settings", {}).get(
                    "enabled", False
                ),
                "patterns": preview_settings.get("regex_settings", {}).get(
                    "patterns", []
                ),
            },
            "whitespace_settings": preview_settings.get(
                "whitespace_settings",
                {
                    "remove_half_space": False,
                    "remove_full_space": False,
                    "remove_newline": False,
                },
            ),
            "tag_special_settings": preview_settings.get(
                "tag_special_settings", {"tag_patterns": []}
            ),
        }

        self.settings_applied.emit(formatted_settings)

    def show_event(self, event):
        super().show_event(event)
        current_width = self.width()
        self.tag_settings_widget.load_settings()
        self.whitespace_settings_widget.load_settings()
        self.aozora_settings_widget.load_settings()
        self.regex_settings_widget.load_settings()
        self.adjustSize()

        if current_width > self.minimumWidth():
            self.setMinimumWidth(current_width)
            if self.width() < current_width:
                self.resize(current_width, self.height())
