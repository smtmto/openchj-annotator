from typing import Any, Dict, Optional

from gui.custom_widgets import CustomCheckBox
from gui.styles import apply_checkbox_style
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout

from config import Config

from .base_settings_widget import BaseSettingsWidget


class WhitespaceSettingsWidget(BaseSettingsWidget):
    config_changed = Signal()

    def __init__(self, parent=None, config: Optional[Config] = None):
        super().__init__(parent, config)
        self._setup_ui()
        self._connect_signals()
        self.load_settings()

    def _setup_ui(self):
        self.frame = self.create_section_frame("空白・改行除去")
        self.frame.setMinimumHeight(70)
        self.frame.setMaximumHeight(70)
        frame_layout = self.frame.layout()
        frame_layout.setContentsMargins(10, 10, 10, 10)

        check_layout = QHBoxLayout()
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_layout.setSpacing(10)

        self.halfwidth_space_check = CustomCheckBox("空白（半角）")
        apply_checkbox_style(self.halfwidth_space_check)
        check_layout.addWidget(self.halfwidth_space_check)

        self.fullwidth_space_check = CustomCheckBox("空白（全角）")
        apply_checkbox_style(self.fullwidth_space_check)
        check_layout.addWidget(self.fullwidth_space_check)

        self.newline_check = CustomCheckBox("改行（LF, CRLF）")
        apply_checkbox_style(self.newline_check)
        check_layout.addWidget(self.newline_check)

        check_layout.addStretch()
        frame_layout.addLayout(check_layout)

        self.main_layout.addWidget(self.frame)

    def _connect_signals(self):
        self.halfwidth_space_check.stateChanged.connect(
            lambda state: self._on_whitespace_setting_changed(
                "remove_half_space", state
            )
        )
        self.fullwidth_space_check.stateChanged.connect(
            lambda state: self._on_whitespace_setting_changed(
                "remove_full_space", state
            )
        )
        self.newline_check.stateChanged.connect(
            lambda state: self._on_whitespace_setting_changed("remove_newline", state)
        )

    def load_settings(self):
        if not self.config:
            self.halfwidth_space_check.setChecked(False)
            self.fullwidth_space_check.setChecked(False)
            self.newline_check.setChecked(False)
            return

        config_dict = self.config.config
        output_settings = config_dict.get("output_settings", {})

        self.halfwidth_space_check.setChecked(
            output_settings.get("remove_half_space", False)
        )
        self.fullwidth_space_check.setChecked(
            output_settings.get("remove_full_space", False)
        )
        self.newline_check.setChecked(output_settings.get("remove_newline", False))

    def _on_whitespace_setting_changed(self, setting_key: str, state: int):
        is_enabled = state == 2
        self._save_config_value(["output_settings", setting_key], is_enabled)
        self.config_changed.emit()

    def get_current_settings(self) -> Dict[str, Any]:
        return {
            "whitespace_settings": {
                "remove_half_space": self.halfwidth_space_check.isChecked(),
                "remove_full_space": self.fullwidth_space_check.isChecked(),
                "remove_newline": self.newline_check.isChecked(),
            }
        }

    def clear_settings(self):
        self.halfwidth_space_check.setChecked(False)
        self.fullwidth_space_check.setChecked(False)
        self.newline_check.setChecked(False)

        if self.config:
            self._save_config_value(["output_settings", "remove_half_space"], False)
            self._save_config_value(["output_settings", "remove_full_space"], False)
            self._save_config_value(["output_settings", "remove_newline"], False)

        self.config_changed.emit()
