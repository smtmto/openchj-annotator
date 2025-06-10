import logging
from typing import Any, Dict, List, Optional, Tuple

from gui.components.tag_special_settings_widget import TagSpecialSettingsWidget
from gui.custom_widgets import CustomCheckBox
from gui.styles import (apply_checkbox_style, apply_frame_style,
                        apply_label_style)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from config import Config

from .base_settings_widget import BaseSettingsWidget


class TagSettingsWidget(BaseSettingsWidget):
    config_changed = Signal()

    def __init__(self, parent=None, config: Optional[Config] = None):
        super().__init__(parent, config)
        self.tag_special_settings_visible = False
        self._setup_ui()
        self._connect_signals()
        self.load_settings()

    def _setup_ui(self):
        self.frame = self.create_section_frame("タグ除去")
        frame_layout = self.frame.layout()
        frame_layout.setSpacing(5)

        enable_layout = QHBoxLayout()
        enable_layout.setContentsMargins(0, 0, 0, 0)
        self.tag_enable_check = CustomCheckBox("タグ除去を有効にする")
        apply_checkbox_style(self.tag_enable_check)
        self.tag_enable_check.setMinimumWidth(150)
        enable_layout.addWidget(self.tag_enable_check)
        enable_layout.addSpacing(30)

        self.keep_content_check = CustomCheckBox("タグの内側の文字列を残す")
        apply_checkbox_style(self.keep_content_check)
        self.keep_content_check.setMinimumWidth(180)
        enable_layout.addWidget(self.keep_content_check)
        enable_layout.addStretch()
        frame_layout.addLayout(enable_layout)

        tag_types_widget = QWidget()
        tag_types_layout = QGridLayout(tag_types_widget)
        tag_types_layout.setContentsMargins(0, 5, 0, 0)
        tag_types_layout.setHorizontalSpacing(20)
        tag_types_layout.setVerticalSpacing(5)

        half_width_label = QLabel("半角")
        apply_label_style(half_width_label, "header_bold")
        half_width_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tag_types_layout.addWidget(half_width_label, 0, 0, 1, 2)

        full_width_label = QLabel("全角")
        apply_label_style(full_width_label, "header_bold")
        full_width_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tag_types_layout.addWidget(full_width_label, 0, 2, 1, 2)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        apply_frame_style(separator, "separator")
        separator.setFixedWidth(1)
        tag_types_layout.addWidget(separator, 1, 2, 4, 1)

        self.tag_checkboxes: Dict[str, CustomCheckBox] = {}
        all_tags: List[Tuple[str, str]] = [
            ("<>", "< >"),
            ("()", "( )"),
            ("[]", " [ ]"),
            ("{}", "{ }"),
            ("＜＞", "＜＞"),
            ("（）", "（）"),
            ("［］", "［］"),
            ("｛｝", "｛｝"),
            ("【】", "  【】"),
            ("《》", "  《》"),
        ]
        half_width_tags = all_tags[:4]
        full_width_tags = all_tags[4:]

        for i, (key, label) in enumerate(half_width_tags):
            row, col = i // 2 + 1, i % 2
            cb = CustomCheckBox(label)
            apply_checkbox_style(cb)
            self.tag_checkboxes[key] = cb
            tag_types_layout.addWidget(cb, row, col)

        for i, (key, label) in enumerate(full_width_tags):
            row, col = i // 2 + 1, i % 2 + 3
            cb = CustomCheckBox(label)
            apply_checkbox_style(cb)
            self.tag_checkboxes[key] = cb
            tag_types_layout.addWidget(cb, row, col)

        frame_layout.addWidget(tag_types_widget)

        tag_special_settings_header = QHBoxLayout()
        tag_special_settings_header.setContentsMargins(0, 5, 0, 0)
        tag_special_settings_header.addStretch()
        self.tag_special_toggle_button = QPushButton("タグ特別設定 ▽")
        self.tag_special_toggle_button.setCheckable(True)
        self.tag_special_toggle_button.setFocusPolicy(Qt.NoFocus)
        tag_special_settings_header.addWidget(self.tag_special_toggle_button)
        frame_layout.addLayout(tag_special_settings_header)

        self.tag_special_settings_widget = TagSpecialSettingsWidget()
        self.tag_special_settings_widget.setVisible(False)
        self.tag_special_settings_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        frame_layout.addWidget(self.tag_special_settings_widget)

        self.main_layout.addWidget(self.frame)
        self.main_layout.setSpacing(2)

    def _connect_signals(self):
        self.tag_enable_check.stateChanged.connect(
            self._on_tag_enable_changed_and_update_dependent_controls
        )
        self.keep_content_check.stateChanged.connect(self._on_tag_mode_changed)
        for key, cb in self.tag_checkboxes.items():
            cb.stateChanged.connect(
                lambda state, tag_key=key: self._on_tag_type_changed(tag_key, state)
            )
        self.tag_special_toggle_button.clicked.connect(
            self._toggle_tag_special_settings
        )
        self.tag_special_settings_widget.config_changed.connect(
            self._on_tag_special_settings_changed_and_update_dependent_controls
        )

    def _on_tag_enable_changed_and_update_dependent_controls(self, state: int):
        is_enabled = state == 2
        self._save_config_value(["remove_tags", "enabled"], is_enabled)
        self._toggle_general_tag_controls()
        self.config_changed.emit()

    def _on_tag_special_settings_changed_and_update_dependent_controls(self):
        if not self.config or not self.tag_special_settings_widget:
            return

        tag_special_settings = self.tag_special_settings_widget.get_config()
        self._save_config_value(["tag_special_settings"], tag_special_settings)
        self._update_tag_special_toggle_button()
        self._toggle_general_tag_controls()
        self.config_changed.emit()

    def _toggle_general_tag_controls(
        self,
    ):

        patterns_count = 0
        if self.tag_special_settings_widget:
            config_data = self.tag_special_settings_widget.get_config()
            patterns_count = len(config_data.get("tag_patterns", []))

        has_special_patterns = patterns_count > 0

        if has_special_patterns:

            self.tag_enable_check.setChecked(False)
            self.tag_enable_check.setEnabled(False)
            self.tag_enable_check.setToolTip(
                "タグ特別設定が有効なため、一般タグ除去は無効です。"
            )

            self.keep_content_check.setEnabled(False)
            for cb in self.tag_checkboxes.values():
                cb.setEnabled(False)
        else:

            self.tag_enable_check.setEnabled(True)
            self.tag_enable_check.setToolTip("")

            general_tag_removal_enabled = self.tag_enable_check.isChecked()
            self.keep_content_check.setEnabled(general_tag_removal_enabled)
            for cb in self.tag_checkboxes.values():
                cb.setEnabled(general_tag_removal_enabled)

    def load_settings(self):
        if not self.config:
            self._update_ui_state(
                {"enabled": False, "types": [], "mode": "remove_with_content"},
                {"tag_patterns": []},
            )

            self._toggle_general_tag_controls()
            return

        config_dict = self.config.config
        tag_settings = config_dict.get(
            "remove_tags",
            {"enabled": False, "types": [], "mode": "remove_with_content"},
        )
        tag_special_settings = config_dict.get(
            "tag_special_settings", {"tag_patterns": []}
        )
        self._update_ui_state(tag_settings, tag_special_settings)

        self._toggle_general_tag_controls()

    def _update_ui_state(self, tag_settings, tag_special_settings):

        self.tag_special_settings_widget.set_config(tag_special_settings)
        has_patterns = len(tag_special_settings.get("tag_patterns", [])) > 0
        self.tag_special_settings_visible = has_patterns
        self.tag_special_settings_widget.setVisible(self.tag_special_settings_visible)
        self.tag_special_toggle_button.setChecked(self.tag_special_settings_visible)
        self._update_tag_special_toggle_button()

        self.tag_enable_check.setChecked(tag_settings.get("enabled", False))
        is_keep_content = (
            tag_settings.get("mode", "remove_with_content") == "remove_tags_only"
        )
        self.keep_content_check.setChecked(is_keep_content)
        enabled_tags = tag_settings.get("types", [])
        for key, cb in self.tag_checkboxes.items():
            cb.setChecked(key in enabled_tags)

    def _on_tag_enable_changed(self, state: int):
        is_enabled = state == 2
        self._save_config_value(["remove_tags", "enabled"], is_enabled)
        self._toggle_controls()
        self.config_changed.emit()

    def _on_tag_mode_changed(self, state: int):
        keep_content = state == 2
        mode = "remove_tags_only" if keep_content else "remove_with_content"
        self._save_config_value(["remove_tags", "mode"], mode)
        self.config_changed.emit()

    def _on_tag_type_changed(self, tag_type: str, state: int):
        if not self.config:
            logging.warning("Config is None in _on_tag_type_changed")
            return

        is_checked = state == 2
        tag_settings = self.config.config.setdefault("remove_tags", {})
        current_types = tag_settings.setdefault("types", [])

        new_types = list(current_types)
        if is_checked and tag_type not in new_types:
            new_types.append(tag_type)
        elif not is_checked and tag_type in new_types:
            new_types.remove(tag_type)

        self._save_config_value(["remove_tags", "types"], new_types)
        self.config_changed.emit()

    def _on_tag_special_settings_changed(self):
        if not self.config or not self.tag_special_settings_widget:
            return

        tag_special_settings = self.tag_special_settings_widget.get_config()
        self._save_config_value(["tag_special_settings"], tag_special_settings)
        self._update_tag_special_toggle_button()
        self.config_changed.emit()

    def _toggle_tag_special_settings(self):
        self.tag_special_settings_visible = not self.tag_special_settings_visible
        self.tag_special_toggle_button.setChecked(self.tag_special_settings_visible)
        self._update_tag_special_toggle_button()

        frame_layout = self.frame.layout()
        if frame_layout and isinstance(frame_layout, QVBoxLayout):
            current_width = self.frame.width()
            self.frame.setMinimumWidth(current_width)

        self.tag_special_settings_widget.setVisible(self.tag_special_settings_visible)
        if hasattr(self.parent(), "adjustSize"):
            self.parent().adjustSize()

    def _update_tag_special_toggle_button(self):
        patterns_count = 0
        if self.tag_special_settings_widget:
            config_data = self.tag_special_settings_widget.get_config()
            patterns_count = len(config_data.get("tag_patterns", []))

        has_patterns = patterns_count > 0
        arrow = "△" if self.tag_special_settings_visible else "▽"
        button_text = f"タグ特別設定{'・適用中' if has_patterns else ''} {arrow}"

        base_style = (
            "QPushButton {{ background-color: {bg}; border: 1px solid #ccc; "
            "border-radius: 3px; padding: 3px 8px; font-size: 11px; }}"
            "QPushButton:hover {{ background-color: {hover_bg}; }}"
        )
        if has_patterns:
            style = base_style.format(bg="#e0f0e0", hover_bg="#d0e8d0")
        else:
            style = base_style.format(bg="white", hover_bg="#f8f8f8")

        self.tag_special_toggle_button.setStyleSheet(style)
        self.tag_special_toggle_button.setText(button_text)

    def get_current_settings(self) -> Dict[str, Any]:
        tag_settings = {
            "enabled": self.tag_enable_check.isChecked(),
            "mode": (
                "remove_tags_only"
                if self.keep_content_check.isChecked()
                else "remove_with_content"
            ),
            "types": [key for key, cb in self.tag_checkboxes.items() if cb.isChecked()],
        }

        tag_special_settings = (
            self.tag_special_settings_widget.get_config()
            if self.tag_special_settings_widget
            else {"tag_patterns": []}
        )

        return {
            "tag_settings": tag_settings,
            "tag_special_settings": tag_special_settings,
        }

    def clear_settings(self):
        default_tag_settings = {
            "enabled": False,
            "types": [],
            "mode": "remove_with_content",
        }

        self.tag_special_settings_widget.clear_patterns()
        self._update_ui_state(default_tag_settings, {"tag_patterns": []})

        if self.config:
            self._save_config_value(["remove_tags"], default_tag_settings)
            self._save_config_value(["tag_special_settings"], {"tag_patterns": []})

        self.config_changed.emit()
