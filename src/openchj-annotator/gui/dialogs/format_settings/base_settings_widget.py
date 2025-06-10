import logging
from typing import Any, Dict, Optional

from gui.styles import apply_label_style
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from config import Config


class BaseSettingsWidget(QWidget):
    config_changed = Signal()

    def __init__(self, parent=None, config: Optional[Config] = None):
        super().__init__(parent)
        self.config = config
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_section_frame(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(
            "QFrame { border: 1px solid #C0C0C0; border-radius: 0px; background-color: #F0F0F0; }"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        header_layout = QHBoxLayout()
        label = QLabel(title)
        apply_label_style(label, "header_bold")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        return frame

    def load_settings(self) -> None:
        pass

    def save_settings(self) -> None:
        pass

    def get_current_settings(self) -> Dict[str, Any]:
        return {}

    def _save_config_value(self, keys: list, value: Any) -> None:
        if not self.config:
            logging.warning(
                f"{self.__class__.__name__}._save_config_value: config is None"
            )
            return

        config_dict = self.config.config
        try:
            current_level = config_dict
            for key in keys[:-1]:
                current_level = current_level.setdefault(key, {})
                if not isinstance(current_level, dict):
                    logging.warning(
                        f"Value of '{key}' is not a dictionary. Overwriting."
                    )
                    parent_key = (
                        keys[keys.index(key) - 1] if keys.index(key) > 0 else None
                    )
                    if parent_key:
                        config_dict[parent_key][key] = {}
                        current_level = config_dict[parent_key][key]
                    else:
                        config_dict[key] = {}
                        current_level = config_dict[key]

            last_key = keys[-1]
            current_level[last_key] = value
            self.config.save()

        except Exception as e:
            error_message = f"設定値 ({' -> '.join(keys)} = {value}) の保存中にエラーが発生しました: {e}"
            logging.error(error_message)

    def clear_settings(self) -> None:
        pass
