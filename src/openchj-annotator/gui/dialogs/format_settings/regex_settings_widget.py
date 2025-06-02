import logging
import re
from typing import Any, Dict, Optional

from gui.custom_widgets import CustomCheckBox
from gui.dialogs.regex_help_dialog import show_regex_help_dialog
from gui.styles import (HELP_BUTTON_FIXED_SIZE, HELP_BUTTON_STYLESHEET,
                        apply_button_style, apply_checkbox_style,
                        apply_input_style, apply_label_style,
                        apply_regex_settings_style)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)
from utils.path_manager import get_resource_path

from config import Config

from .base_settings_widget import BaseSettingsWidget


class RegexSettingsWidget(BaseSettingsWidget):
    config_changed = Signal()

    def __init__(self, parent=None, config: Optional[Config] = None):
        super().__init__(parent, config)
        self.current_regex_patterns = []
        self._setup_ui()
        self._connect_signals()
        self.load_settings()

    def _setup_ui(self):
        self.frame = self.create_section_frame("正規表現設定")
        frame_layout = self.frame.layout()
        header_layout = frame_layout.itemAt(0).layout()
        self.regex_help_button = QPushButton("?")
        self.regex_help_button.setStyleSheet(HELP_BUTTON_STYLESHEET)
        self.regex_help_button.setFixedSize(*HELP_BUTTON_FIXED_SIZE)
        self.regex_help_button.setToolTip("正規表現のヘルプ")
        header_layout.insertWidget(1, self.regex_help_button)

        self.regex_enable_check = CustomCheckBox("正規表現による置換を有効にする")
        apply_checkbox_style(self.regex_enable_check)
        frame_layout.addWidget(self.regex_enable_check)

        patterns_widget = QWidget()
        patterns_layout = QGridLayout(patterns_widget)
        patterns_layout.setContentsMargins(0, 5, 0, 0)
        patterns_layout.setHorizontalSpacing(10)
        patterns_layout.setVerticalSpacing(5)

        pattern_label = QLabel("パターン:")
        apply_label_style(pattern_label)
        apply_regex_settings_style(pattern_label, "pattern_label")
        patterns_layout.addWidget(pattern_label, 0, 0)

        self.pattern_entry = QLineEdit()
        self.pattern_entry.setPlaceholderText("正規表現パターン")
        apply_input_style(self.pattern_entry)
        apply_regex_settings_style(self.pattern_entry, "pattern_entry")
        patterns_layout.addWidget(self.pattern_entry, 0, 1)

        replacement_label = QLabel("置換後の文字列:")
        apply_label_style(replacement_label)
        apply_regex_settings_style(replacement_label, "pattern_label")
        patterns_layout.addWidget(replacement_label, 0, 2)

        self.replacement_entry = QLineEdit()
        self.replacement_entry.setPlaceholderText("削除の場合は空欄")
        apply_input_style(self.replacement_entry)
        apply_regex_settings_style(self.replacement_entry, "pattern_entry")
        patterns_layout.addWidget(self.replacement_entry, 0, 3)

        self.regex_add_button = QPushButton("追加")
        apply_button_style(self.regex_add_button, "secondary")
        self.regex_add_button.setFixedHeight(24)
        apply_regex_settings_style(self.regex_add_button, "add_button")
        patterns_layout.addWidget(self.regex_add_button, 0, 4, Qt.AlignVCenter)

        frame_layout.addWidget(patterns_widget)

        self.pattern_rows_widget = QWidget()
        self.pattern_rows_layout = QVBoxLayout(self.pattern_rows_widget)
        self.pattern_rows_layout.setContentsMargins(0, 5, 0, 0)
        self.pattern_rows_layout.setSpacing(3)
        frame_layout.addWidget(self.pattern_rows_widget)

        self.main_layout.addWidget(self.frame)

    def _connect_signals(self):
        self.regex_enable_check.stateChanged.connect(self._on_regex_enable_changed)
        self.regex_add_button.clicked.connect(self._add_regex_pattern)
        self.regex_help_button.clicked.connect(self._show_regex_help)

    def load_settings(self):
        if not self.config:
            self.regex_enable_check.setChecked(False)
            self.current_regex_patterns = []
            self._update_patterns_list()
            self._toggle_controls()
            return

        config_dict = self.config.config
        regex_settings = config_dict.get("regex_settings", {})
        if not regex_settings:
            regex_settings = {"enabled": False, "patterns": []}

        self.regex_enable_check.setChecked(regex_settings.get("enabled", False))
        self.current_regex_patterns = list(regex_settings.get("patterns", []))
        self._update_patterns_list()
        self._toggle_controls()

    def _on_regex_enable_changed(self, state: int):
        is_enabled = state == 2
        self._save_config_value(["regex_settings", "enabled"], is_enabled)
        self._toggle_controls()
        self.config_changed.emit()

    def _add_regex_pattern(self):
        pattern_str = self.pattern_entry.text().strip()
        replacement_str = self.replacement_entry.text()

        if not pattern_str:
            QMessageBox.warning(
                self, "入力エラー", "正規表現パターンを入力してください。"
            )
            return

        try:
            re.compile(pattern_str)
        except re.error as e:
            QMessageBox.warning(
                self, "正規表現エラー", f"入力されたパターンは無効です:\n{e}"
            )
            return

        if len(self.current_regex_patterns) >= 5:
            QMessageBox.warning(
                self, "制限エラー", "正規表現パターンの登録は最大5つまでです。"
            )
            return

        new_pattern_data = {
            "pattern": pattern_str,
            "replacement": replacement_str,
            "enabled": True,
        }

        self.current_regex_patterns.append(new_pattern_data)
        self._save_config_value(
            ["regex_settings", "patterns"], self.current_regex_patterns
        )
        self._update_patterns_list()
        self.pattern_entry.clear()
        self.replacement_entry.clear()
        self._toggle_controls()
        self.config_changed.emit()

    def _delete_pattern(self, index: int):
        if 0 <= index < len(self.current_regex_patterns):
            del self.current_regex_patterns[index]
            self._save_config_value(
                ["regex_settings", "patterns"], self.current_regex_patterns
            )
            self._update_patterns_list()
            self._toggle_controls()
            self.config_changed.emit()

    def _update_patterns_list(self):
        while self.pattern_rows_layout.count():
            item = self.pattern_rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.current_regex_patterns:
            for i, pattern_data in enumerate(self.current_regex_patterns):
                self._add_pattern_row(i, pattern_data)

    def _add_pattern_row(self, index: int, pattern_data: Dict[str, Any]):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        num_label = QLabel(f"({index + 1})")
        num_label.setFixedWidth(30)
        num_label.setAlignment(Qt.AlignCenter)
        num_label.setStyleSheet("QLabel { color: #444; border: none; }")
        row_layout.addWidget(num_label)

        replacement_display = pattern_data.get("replacement", "")
        if not replacement_display:
            replacement_display = "（削除）"

        display_text = f"{pattern_data.get('pattern','(空)')} → {replacement_display}"
        pattern_display_edit = QLineEdit(display_text)
        pattern_display_edit.setReadOnly(True)
        apply_regex_settings_style(pattern_display_edit, "pattern_display")
        row_layout.addWidget(pattern_display_edit)

        delete_btn = QPushButton("✕")
        apply_button_style(delete_btn, "secondary")
        delete_btn.setFixedSize(20, 20)
        apply_regex_settings_style(delete_btn, "delete_button")
        delete_btn.setToolTip("このパターンを削除")
        delete_btn.clicked.connect(lambda _, idx=index: self._delete_pattern(idx))
        row_layout.addWidget(delete_btn)

        self.pattern_rows_layout.addWidget(row_widget)

    def _toggle_controls(self):
        regex_enabled = self.regex_enable_check.isChecked()
        max_patterns_reached = len(self.current_regex_patterns) >= 5
        can_add_patterns = regex_enabled and not max_patterns_reached

        self.pattern_entry.setEnabled(can_add_patterns)
        self.replacement_entry.setEnabled(can_add_patterns)
        self.regex_add_button.setEnabled(can_add_patterns)

        for i in range(self.pattern_rows_layout.count()):
            item = self.pattern_rows_layout.itemAt(i)
            if item and item.widget():
                row_widget = item.widget()
                row_widget.setEnabled(regex_enabled)

                try:
                    row_layout = row_widget.layout()
                    if row_layout and row_layout.count() > 2:
                        delete_button = row_layout.itemAt(
                            row_layout.count() - 1
                        ).widget()
                        if isinstance(delete_button, QPushButton):
                            delete_button.setEnabled(regex_enabled)
                        pattern_edit = row_layout.itemAt(1).widget()
                        if isinstance(pattern_edit, QLineEdit):
                            if regex_enabled:
                                apply_regex_settings_style(
                                    pattern_edit, "enabled_entry"
                                )
                            else:
                                apply_regex_settings_style(
                                    pattern_edit, "disabled_entry"
                                )
                except Exception as e:
                    logging.warning(f"pattern_row {i} toggle_controls: {e}")

        self._apply_regex_control_styles(regex_enabled, max_patterns_reached)

    def _apply_regex_control_styles(
        self, regex_enabled: bool, max_patterns_reached: bool
    ):
        can_add_patterns = regex_enabled and not max_patterns_reached

        if can_add_patterns:
            apply_regex_settings_style(self.pattern_entry, "enabled_entry")
            apply_regex_settings_style(self.replacement_entry, "enabled_entry")
            apply_regex_settings_style(self.regex_add_button, "enabled_add_button")

            self.pattern_entry.setPlaceholderText("正規表現パターン")
            self.replacement_entry.setPlaceholderText("削除の場合は空欄")
        else:
            apply_regex_settings_style(self.pattern_entry, "disabled_entry")
            apply_regex_settings_style(self.replacement_entry, "disabled_entry")
            apply_regex_settings_style(self.regex_add_button, "disabled_add_button")

            if max_patterns_reached and regex_enabled:
                self.pattern_entry.setPlaceholderText("パターンは5つまで")
                self.replacement_entry.setPlaceholderText("パターンは5つまで")
            elif not regex_enabled:
                self.pattern_entry.setPlaceholderText("正規表現が無効です")
                self.replacement_entry.setPlaceholderText("正規表現が無効です")
            else:
                self.pattern_entry.setPlaceholderText("追加不可")
                self.replacement_entry.setPlaceholderText("追加不可")

    def _show_regex_help(self):
        try:
            html_path = get_resource_path("help", "regex_help.html")

            if not html_path.exists():
                raise FileNotFoundError(f"ヘルプファイルが見つかりません: {html_path}")
            show_regex_help_dialog(self, str(html_path))

        except ImportError:
            QMessageBox.warning(
                self,
                "エラー",
                "ヘルプ表示に必要なモジュール (regex_help_dialog) が見つかりません。",
            )
        except FileNotFoundError as e:
            QMessageBox.warning(self, "ファイルエラー", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, "エラー", f"ヘルプ表示中に予期せぬエラーが発生しました:\n{e}"
            )

    def get_current_settings(self) -> Dict[str, Any]:
        return {
            "regex_settings": {
                "enabled": self.regex_enable_check.isChecked(),
                "patterns": list(self.current_regex_patterns),
            }
        }

    def clear_settings(self):
        default_regex_settings = {"enabled": False, "patterns": []}

        self.regex_enable_check.setChecked(False)
        self.current_regex_patterns = []
        self._update_patterns_list()
        self.pattern_entry.clear()
        self.replacement_entry.clear()
        self._toggle_controls()

        if self.config:
            self._save_config_value(["regex_settings"], default_regex_settings)

        self.config_changed.emit()
