from typing import Any, Dict, Optional

from gui.custom_widgets import CustomCheckBox
from gui.styles import apply_checkbox_style, apply_label_style
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel

from config import Config

from .base_settings_widget import BaseSettingsWidget


class AozoraSettingsWidget(BaseSettingsWidget):
    config_changed = Signal()

    def __init__(self, parent=None, config: Optional[Config] = None):
        super().__init__(parent, config)
        self._setup_ui()
        self._connect_signals()
        self.load_settings()

    def _setup_ui(self):
        self.frame = self.create_section_frame("青空文庫")
        self.frame.setMinimumHeight(90)
        self.frame.setFixedHeight(90)
        frame_layout = self.frame.layout()

        self.aozora_check = CustomCheckBox("青空文庫形式のテキストから注記・空白を一括除去する")
        apply_checkbox_style(self.aozora_check)
        frame_layout.addWidget(self.aozora_check)

        aozora_info = QLabel(
            "ルビ《 》　 冒頭・末尾の注記　 本文注記［ ］ 〔 〕　 空白（半角・全角）"
        )
        apply_label_style(aozora_info, "info")
        aozora_info.setStyleSheet("margin-left: 20px; border: none;")
        frame_layout.addWidget(aozora_info)

        self.main_layout.addWidget(self.frame)

    def _connect_signals(self):
        self.aozora_check.stateChanged.connect(self._on_aozora_setting_changed)

    def load_settings(self):
        if not self.config:
            self.aozora_check.setChecked(False)
            return

        config_dict = self.config.config
        aozora_cleanup = config_dict.get("aozora_cleanup", False)
        self.aozora_check.setChecked(aozora_cleanup)

    def _on_aozora_setting_changed(self, state: int):
        is_enabled = state == 2
        self._save_config_value(["aozora_cleanup"], is_enabled)
        self.config_changed.emit()

    def get_current_settings(self) -> Dict[str, Any]:
        return {"aozora_cleanup": self.aozora_check.isChecked()}

    def clear_settings(self):
        self.aozora_check.setChecked(False)

        if self.config:
            self._save_config_value(["aozora_cleanup"], False)

        self.config_changed.emit()
