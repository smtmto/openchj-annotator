import copy
import os
import re
from typing import Optional

from gui.custom_widgets import CustomCheckBox
from gui.styles import (
    apply_button_style,
    apply_checkbox_style,
    apply_combobox_style,
    apply_input_style,
    apply_label_style,
    get_combo_style,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from utils.file_utils import get_downloads_directory

from config import Config

from .dictionary_settings_widget import DictionarySettingsWidget


class OutputSettingsFrame(QWidget):
    def __init__(
        self,
        parent: QWidget,
        config: Config,
        dictionary_settings: DictionarySettingsWidget,
    ):
        super().__init__(parent)
        self.config = config
        self.dictionary_settings = dictionary_settings
        self._loading_settings = False
        self._last_default_suffix = None
        self.setup_ui()
        self.load_settings()
        self._last_default_suffix = self._get_default_suffix()
        self.dictionary_settings.dictionary_changed.connect(self.update_default_suffix)
        self._update_suffix_buttons_state()

    def _update_suffix_buttons_state(self):
        current_text = self.suffix_input.text()
        date_tail_pattern = r"(_(YYYYMMDD(_HHMMSS)?|HHMMSS|\d{8}((_|\-)\d{6})?|\d{6}))$"
        has_date = re.search(date_tail_pattern, current_text, re.IGNORECASE) is not None
        self.clear_suffix_button.setEnabled(has_date)
        self.add_date_button.setEnabled(not has_date)

    def clear_directory(self):

        settings = self.config.config.get("output_settings", {})
        settings["use_custom_output_dir"] = False
        settings["output_directory"] = ""
        self.config.config["output_settings"] = settings
        self.config.save()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        format_group = QGroupBox("出力形式")
        format_group.setMinimumHeight(60)
        format_layout = QVBoxLayout(format_group)
        format_layout.setContentsMargins(10, 5, 10, 5)

        format_info = QLabel(
            "ファイル拡張子: .txt　内容形式: TSV　エンコーディング: UTF-8 (BOMなし)　改行コード: LF"
        )
        apply_label_style(format_info)
        format_layout.addWidget(format_info)

        layout.addWidget(format_group)
        layout.addSpacing(5)

        folder_group = QGroupBox("入力ディレクトリ処理設定")
        folder_group.setMinimumHeight(60)
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setContentsMargins(10, 5, 10, 5)

        self.include_subfolders_checkbox = CustomCheckBox(
            "入力フォルダを再帰的に処理する（サブフォルダも含めて処理）"
        )
        self.include_subfolders_checkbox.setChecked(False)
        self.include_subfolders_checkbox.stateChanged.connect(self.on_settings_changed)
        apply_checkbox_style(self.include_subfolders_checkbox, "smaller_font")

        folder_layout.addWidget(self.include_subfolders_checkbox)

        layout.addWidget(folder_group)
        layout.addSpacing(5)

        naming_group = QGroupBox("出力ファイル名規則")
        naming_group.setMinimumHeight(110)
        naming_layout = QVBoxLayout(naming_group)
        naming_layout.setContentsMargins(10, 10, 10, 15)

        filename_layout = QHBoxLayout()
        filename_layout.setSpacing(5)
        filename_layout.setContentsMargins(0, 0, 0, 5)

        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("プレフィックス")
        self.prefix_input.setFixedHeight(24)
        apply_input_style(self.prefix_input)
        self.prefix_input.textChanged.connect(self.on_settings_changed)
        self.prefix_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        filename_layout.addWidget(self.prefix_input, 1, Qt.AlignVCenter)

        filename_label = QLabel("{入力ファイル名}")
        apply_label_style(filename_label, "filename")
        filename_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        filename_layout.addWidget(filename_label, 0, Qt.AlignVCenter)

        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText(
            f"サフィックス（デフォルト: {self._get_default_suffix()}）"
        )
        self.suffix_input.setFixedHeight(24)
        apply_input_style(self.suffix_input)
        self.suffix_input.setReadOnly(True)
        self.suffix_input.setFocusPolicy(Qt.NoFocus)
        self.suffix_input.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.suffix_input.textChanged.connect(self._on_suffix_changed)
        self.suffix_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        filename_layout.addWidget(self.suffix_input, 4, Qt.AlignVCenter)

        self.add_date_button = QPushButton("日時追加")
        self.add_date_button.setFixedHeight(24)
        apply_button_style(self.add_date_button, "config")
        self.add_date_button.clicked.connect(self.add_datetime_to_suffix)
        filename_layout.addWidget(self.add_date_button, 0, Qt.AlignVCenter)

        self.clear_suffix_button = QPushButton("クリア")
        self.clear_suffix_button.setFixedHeight(24)
        apply_button_style(self.clear_suffix_button, "secondary")
        self.clear_suffix_button.clicked.connect(self.clear_datetime_from_suffix)
        filename_layout.addWidget(self.clear_suffix_button, 0, Qt.AlignVCenter)
        filename_layout.setAlignment(Qt.AlignCenter)
        naming_layout.addLayout(filename_layout)

        self.filename_preview = QLabel()
        self.filename_preview.setFixedHeight(20)
        apply_label_style(self.filename_preview)
        naming_layout.addWidget(self.filename_preview, 0, Qt.AlignBottom)

        layout.addWidget(naming_group)
        layout.addSpacing(5)

        directory_group = QGroupBox("出力先設定")
        directory_group.setMinimumHeight(130)
        directory_layout = QVBoxLayout(directory_group)
        directory_layout.setContentsMargins(10, 10, 10, 10)

        output_dir_combo_layout = QGridLayout()
        output_dir_combo_layout.setColumnStretch(1, 1)
        output_dir_combo_layout.setHorizontalSpacing(10)

        output_dir_label = QLabel("現在の出力先:")
        apply_label_style(output_dir_label)
        output_dir_label.setMinimumWidth(120)
        output_dir_combo_layout.addWidget(output_dir_label, 0, 0, Qt.AlignLeft)

        self.output_dir_combo = QComboBox()
        apply_combobox_style(self.output_dir_combo)
        downloads_dir = get_downloads_directory()
        self.output_dir_combo.addItem(
            f"デフォルト（ダウンロードフォルダ: {os.path.basename(downloads_dir)}）"
        )
        self.output_dir_combo.addItem("ユーザー設定出力先（未指定）")
        self.output_dir_combo.currentIndexChanged.connect(
            self.on_output_dir_type_changed
        )

        self.output_dir_combo.showPopup = self._custom_show_popup
        self.output_dir_combo.setStyleSheet(get_combo_style())
        output_dir_combo_layout.addWidget(self.output_dir_combo, 0, 1)
        directory_layout.addLayout(output_dir_combo_layout)

        output_dir_path_layout = QGridLayout()
        output_dir_path_layout.setColumnStretch(1, 1)
        output_dir_path_layout.setHorizontalSpacing(10)
        output_dir_path_layout.setVerticalSpacing(0)

        output_dir_path_label = QLabel("ユーザー設定出力先:")
        apply_label_style(output_dir_path_label)
        output_dir_path_label.setMinimumWidth(120)
        output_dir_path_layout.addWidget(output_dir_path_label, 0, 0, Qt.AlignLeft)

        self.directory_input = QLineEdit()
        self.directory_input.setReadOnly(True)
        apply_input_style(self.directory_input)
        output_dir_path_layout.addWidget(self.directory_input, 0, 1)

        self.browse_button = QPushButton("選択")
        apply_button_style(self.browse_button, "secondary")
        self.browse_button.clicked.connect(self.browse_directory)

        browse_container = QWidget()
        browse_container_layout = QVBoxLayout(browse_container)
        browse_container_layout.setContentsMargins(0, 0, 0, 0)
        browse_container_layout.addWidget(self.browse_button, 0, Qt.AlignCenter)
        output_dir_path_layout.addWidget(browse_container, 0, 2, Qt.AlignCenter)

        self.clear_button = QPushButton("クリア")
        apply_button_style(self.clear_button, "secondary")
        self.clear_button.clicked.connect(self.clear_directory)

        clear_container = QWidget()
        clear_container_layout = QVBoxLayout(clear_container)
        clear_container_layout.setContentsMargins(0, 0, 0, 0)
        clear_container_layout.addWidget(self.clear_button, 0, Qt.AlignCenter)
        output_dir_path_layout.addWidget(clear_container, 0, 3, Qt.AlignCenter)
        directory_layout.addLayout(output_dir_path_layout)
        try:
            dict_btn_h = self.dictionary_settings.dic_entry.sizeHint().height()
            self.browse_button.setFixedHeight(dict_btn_h)
            self.clear_button.setFixedHeight(dict_btn_h)
        except Exception:
            pass
        layout.addWidget(directory_group)
        layout.addStretch(1)

    def _get_default_suffix(self) -> str:
        return self.dictionary_settings.get_current_suffix()

    def _custom_show_popup(self):
        self._loading_settings = True

        settings = self.config.config.get("output_settings", {})
        custom_dir_from_config = settings.get("output_directory", "")

        self.output_dir_combo.blockSignals(True)

        self.output_dir_combo.clear()
        default_downloads_dir_path = settings.get(
            "default_directory", get_downloads_directory()
        )
        self.output_dir_combo.addItem(
            f"デフォルト（ダウンロードフォルダ: {os.path.basename(default_downloads_dir_path)}）"
        )

        if custom_dir_from_config and os.path.exists(custom_dir_from_config):
            self.output_dir_combo.addItem(
                f"ユーザー設定出力先 ({custom_dir_from_config})"
            )
        use_custom_dir_flag_from_config = settings.get("use_custom_output_dir", False)

        if (
            use_custom_dir_flag_from_config
            and custom_dir_from_config
            and os.path.exists(custom_dir_from_config)
        ):
            if self.output_dir_combo.count() > 1:
                self.output_dir_combo.setCurrentIndex(1)
            else:
                self.output_dir_combo.setCurrentIndex(0)
        else:
            self.output_dir_combo.setCurrentIndex(0)

        self.output_dir_combo.blockSignals(False)
        self._loading_settings = False

        QComboBox.showPopup(self.output_dir_combo)

    def load_settings(self):
        self._loading_settings = True
        try:
            settings = self.config.config.get("output_settings")
            if settings is None:
                settings = copy.deepcopy(
                    Config.DEFAULT_CONFIG.get("output_settings", {})
                )
                if not settings.get("default_directory"):
                    settings["default_directory"] = get_downloads_directory()

            self.prefix_input.setText(settings.get("prefix", ""))

            loaded_suffix = settings.get("suffix")
            if loaded_suffix is None:
                loaded_suffix = self._get_default_suffix()

            self.suffix_input.setText(loaded_suffix)
            self.suffix_input.setPlaceholderText(
                f"サフィックス（デフォルト: {self._get_default_suffix()}）"
            )

            self.include_subfolders_checkbox.setChecked(
                settings.get("include_subfolders", False)
            )

            use_custom_dir_from_config = settings.get("use_custom_output_dir", False)
            custom_dir_from_config = settings.get("output_directory", "")

            self.output_dir_combo.blockSignals(True)
            self.directory_input.blockSignals(True)

            if (
                use_custom_dir_from_config
                and custom_dir_from_config
                and os.path.exists(custom_dir_from_config)
            ):
                self.directory_input.setText(custom_dir_from_config)
                self.directory_input.setEnabled(True)
                self.browse_button.setEnabled(True)
                self.clear_button.setEnabled(True)
                self._repopulate_combobox_items_for_load(
                    default_text=settings.get(
                        "default_directory", get_downloads_directory()
                    ),
                    user_text=custom_dir_from_config,
                )
                self.output_dir_combo.setCurrentIndex(1)

            elif (
                use_custom_dir_from_config
                and custom_dir_from_config
                and not os.path.exists(custom_dir_from_config)
            ):
                self.directory_input.setText(
                    custom_dir_from_config + " (見つかりません)"
                )
                self.directory_input.setEnabled(True)
                self.browse_button.setEnabled(True)
                self.clear_button.setEnabled(True)
                self._repopulate_combobox_items_for_load(
                    default_text=settings.get(
                        "default_directory", get_downloads_directory()
                    ),
                    user_text=custom_dir_from_config,
                )
                self.output_dir_combo.setCurrentIndex(1)

            elif use_custom_dir_from_config and not custom_dir_from_config:
                self.directory_input.setText("未設定")
                self.directory_input.setEnabled(True)
                self.browse_button.setEnabled(True)
                self.clear_button.setEnabled(True)
                self._repopulate_combobox_items_for_load(
                    default_text=settings.get(
                        "default_directory", get_downloads_directory()
                    ),
                    user_text="",
                )
                self.output_dir_combo.setCurrentIndex(1)

            else:
                self.directory_input.setText(
                    custom_dir_from_config if custom_dir_from_config else "未設定"
                )
                self.directory_input.setEnabled(False)
                self.browse_button.setEnabled(True)
                self.clear_button.setEnabled(False)
                self._repopulate_combobox_items_for_load(
                    default_text=settings.get(
                        "default_directory", get_downloads_directory()
                    ),
                    user_text=custom_dir_from_config,
                )
                self.output_dir_combo.setCurrentIndex(0)

            self.directory_input.blockSignals(False)
            self.output_dir_combo.blockSignals(False)
            self.update_filename_preview()
            self._update_suffix_buttons_state()
        finally:
            self._loading_settings = False

    def _repopulate_combobox_items_for_load(
        self, default_text: str, user_text: Optional[str]
    ):
        self.output_dir_combo.clear()
        self.output_dir_combo.addItem(
            f"デフォルト（ダウンロードフォルダ: {os.path.basename(default_text)}）"
        )
        if user_text and os.path.exists(user_text):
            self.output_dir_combo.addItem(f"ユーザー設定出力先 ({user_text})")
        elif user_text and not os.path.exists(user_text):
            self.output_dir_combo.addItem(f"ユーザー設定出力先 ({user_text} - 無効)")
        else:
            self.output_dir_combo.addItem("ユーザー設定出力先（未指定）")

    def on_output_dir_type_changed(self, index: int):
        if self._loading_settings:
            return

        settings = self.config.config.get("output_settings", {})
        is_user_dir_selected_by_combo_action = (
            index == 1 and self.output_dir_combo.count() > 1
        )

        current_custom_path_in_config = settings.get("output_directory", "")

        if is_user_dir_selected_by_combo_action:
            settings["use_custom_output_dir"] = True
            self.directory_input.setText(
                current_custom_path_in_config
                if current_custom_path_in_config
                else "未設定"
            )
            self.directory_input.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.clear_button.setEnabled(bool(current_custom_path_in_config))
        else:
            settings["use_custom_output_dir"] = False
            self.directory_input.setText(
                current_custom_path_in_config
                if current_custom_path_in_config
                else "未設定"
            )
            self.directory_input.setEnabled(False)
            self.browse_button.setEnabled(True)
            self.clear_button.setEnabled(False)

        self.config.config["output_settings"] = settings
        self.config.save()

    def on_settings_changed(self):
        if self._loading_settings:
            return

        settings = self.config.config.get("output_settings", {})

        settings.update(
            {
                "prefix": self.prefix_input.text(),
                "include_subfolders": self.include_subfolders_checkbox.isChecked(),
            }
        )
        self.config.config["output_settings"] = settings
        self.config.save()
        self.update_filename_preview()

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "出力先ディレクトリを選択")
        if directory:
            settings = self.config.config.get("output_settings", {})
            settings["use_custom_output_dir"] = True
            settings["output_directory"] = directory
            self.config.config["output_settings"] = settings
            self.config.save()
            self.load_settings()

    def update_filename_preview(self):
        prefix = self.prefix_input.text()
        suffix_to_display = self.suffix_input.text()
        if not suffix_to_display:
            suffix_to_display = self._get_default_suffix()

        example = f"出力ファイル名:　{prefix}(入力ファイル名){suffix_to_display}.txt"
        self.filename_preview.setText(example)

    def _on_suffix_changed(self, text: str):
        if self._loading_settings:
            return

        current_settings = self.config.config.get("output_settings", {}).copy()
        default_suffix = self._get_default_suffix()
        if not text:
            self.suffix_input.blockSignals(True)
            self.suffix_input.setText(default_suffix)
            self.suffix_input.blockSignals(False)

            current_settings["suffix"] = default_suffix
        else:
            current_settings["suffix"] = text

        self.config.config["output_settings"] = current_settings
        self.config.save()
        self.update_filename_preview()
        self._update_suffix_buttons_state()

    def update_default_suffix(self, new_suffix: str):
        self._loading_settings = True
        self.suffix_input.setPlaceholderText(
            f"サフィックス（デフォルト: {new_suffix}）"
        )

        current_text = self.suffix_input.text()

        date_tail_pattern = r"(_(YYYYMMDD(_HHMMSS)?|HHMMSS|\d{8}((_|\-)\d{6})?|\d{6}))$"
        m = re.search(date_tail_pattern, current_text)
        if m:
            date_tail = m.group(1)
            self.suffix_input.setText(new_suffix + date_tail)
        elif not current_text or (
            self._last_default_suffix is not None
            and current_text == self._last_default_suffix
        ):
            self.suffix_input.setText(new_suffix)

        self._last_default_suffix = new_suffix

        self.update_filename_preview()
        self._loading_settings = False
        self._on_suffix_changed(self.suffix_input.text())

    def clear_datetime_from_suffix(self):
        base_default = self._get_default_suffix()
        self.suffix_input.setText(base_default)
        self._on_suffix_changed(self.suffix_input.text())

    def add_datetime_to_suffix(self):
        current_suffix_in_input = self.suffix_input.text()
        base_suffix = (
            current_suffix_in_input
            if current_suffix_in_input
            else self._get_default_suffix()
        )

        date_tail_pattern = r"(_(YYYYMMDD(_HHMMSS)?|HHMMSS|\d{8}((_|\-)\d{6})?|\d{6}))$"
        if re.search(date_tail_pattern, base_suffix, re.IGNORECASE):
            return

        date_format_placeholder = "_YYYYMMDD_HHMMSS"
        new_suffix = base_suffix + date_format_placeholder
        self.suffix_input.setText(new_suffix)
