import logging
import os

import fugashi
from gui.styles import (
    apply_button_style,
    apply_combobox_style,
    apply_input_style,
    apply_label_style,
    apply_message_box_style,
    get_combo_style,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from utils.file_utils import normalize_path


class DictionarySettingsWidget(QWidget):
    dictionary_changed = Signal(str)
    show_user_dict_help_requested = Signal()
    open_download_page_requested = Signal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.dictionary_info = {}
        self.config = config
        self._calling_from_custom_clear = False
        self._setup_ui()
        self._connect_signals()
        self.update_dictionary_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        dict_layout = QGridLayout()
        dict_layout.setVerticalSpacing(10)
        dict_layout.setColumnStretch(1, 1)

        dict_layout.setContentsMargins(0, 20, 0, 0)
        active_label = QLabel("現在適用中の辞書:")
        apply_label_style(active_label)
        dict_layout.addWidget(active_label, 0, 0, alignment=Qt.AlignTop)
        self.active_dict_combo = QComboBox()
        apply_combobox_style(self.active_dict_combo)
        self.active_dict_combo.setStyleSheet(get_combo_style())
        dict_layout.addWidget(self.active_dict_combo, 0, 1, 1, 3)

        dic_label = QLabel("カスタム辞書\n(dicrc):")
        apply_label_style(dic_label)
        dic_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        dict_layout.addWidget(dic_label, 1, 0, alignment=Qt.AlignTop)
        self.dic_entry = QLineEdit()
        self.dic_entry.setReadOnly(True)
        apply_input_style(self.dic_entry)
        dict_layout.addWidget(self.dic_entry, 1, 1)
        self.dic_button = QPushButton("選択")
        self.dic_button.setFixedHeight(self.dic_entry.sizeHint().height())
        apply_button_style(self.dic_button, "secondary")
        dict_layout.addWidget(self.dic_button, 1, 2, Qt.AlignCenter)
        self.dic_clear_button = QPushButton("クリア")
        self.dic_clear_button.setFixedHeight(self.dic_entry.sizeHint().height())
        apply_button_style(self.dic_clear_button, "secondary")
        dict_layout.addWidget(self.dic_clear_button, 1, 3, Qt.AlignCenter)

        user_dict_label = QLabel("ユーザー辞書\n(.dic):")
        apply_label_style(user_dict_label)
        user_dict_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        dict_layout.addWidget(user_dict_label, 2, 0, alignment=Qt.AlignTop)
        self.user_dict_entry = QLineEdit()
        self.user_dict_entry.setReadOnly(True)
        apply_input_style(self.user_dict_entry)
        dict_layout.addWidget(self.user_dict_entry, 2, 1)
        self.user_dict_button = QPushButton("選択")
        self.user_dict_button.setFixedHeight(self.user_dict_entry.sizeHint().height())
        apply_button_style(self.user_dict_button, "secondary")
        dict_layout.addWidget(self.user_dict_button, 2, 2, Qt.AlignCenter)
        self.user_dict_clear_button = QPushButton("クリア")
        self.user_dict_clear_button.setFixedHeight(
            self.user_dict_entry.sizeHint().height()
        )
        apply_button_style(self.user_dict_clear_button, "secondary")
        dict_layout.addWidget(self.user_dict_clear_button, 2, 3, Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        custom_dict_help_button = QPushButton("カスタム辞書設定方法")
        apply_button_style(custom_dict_help_button, "config")
        button_layout.addWidget(custom_dict_help_button)
        user_dict_help_button = QPushButton("ユーザー辞書設定方法")
        apply_button_style(user_dict_help_button, "config")
        button_layout.addWidget(user_dict_help_button)
        dict_layout.addLayout(button_layout, 3, 0, 1, 4)
        layout.addLayout(dict_layout)
        self.custom_dict_help_button = custom_dict_help_button
        self.user_dict_help_button = user_dict_help_button

    def _connect_signals(self):
        self.active_dict_combo.currentTextChanged.connect(self.on_active_dict_changed)
        self.dic_button.clicked.connect(lambda: self.select_dictionary("dic"))
        self.dic_clear_button.clicked.connect(self.clear_custom_dictionary)
        self.user_dict_button.clicked.connect(self.select_user_dictionary)
        self.user_dict_clear_button.clicked.connect(self.clear_user_dictionary)
        self.custom_dict_help_button.clicked.connect(
            self.open_download_page_requested.emit
        )
        self.user_dict_help_button.clicked.connect(
            self.show_user_dict_help_requested.emit
        )

    def check_dictionary_paths(self):
        changed = False
        custom_dict_path = self.config.get_unidic_path("dic")
        if custom_dict_path and not os.path.exists(custom_dict_path):
            if self.config.get_active_dictionary() == "dic":
                self.config.set_active_dictionary("lite")
                changed = True
            self.config.set_unidic_path("dic", None)
            changed = True

        user_dict_path = self.config.get_user_dictionary_path()
        if user_dict_path and not os.path.exists(user_dict_path):
            pass
        return changed

    def update_dictionary_list(self):
        config_changed = self.check_dictionary_paths()

        self.dictionary_info.clear()
        self.dictionary_info["lite"] = {
            "display_name": "UniDic-Lite（デフォルト）",
            "suffix": "_unidic-lite-1.0.8",
        }
        available_dict_items = {self.dictionary_info["lite"]["display_name"]: "lite"}

        dic_path = self.config.get_unidic_path("dic")
        if dic_path and os.path.exists(dic_path):
            display_name, suffix = self._update_dictionary_info(dic_path)
            if suffix and not suffix.startswith("_"):
                suffix = f"_{suffix}"
            if display_name:
                self.dictionary_info["dic"] = {
                    "display_name": display_name,
                    "suffix": suffix,
                }
                if display_name in available_dict_items:
                    display_name = f"{display_name} (カスタム)"
                available_dict_items[display_name] = "dic"

        current_selection_key = self.config.get_active_dictionary()
        self.active_dict_combo.blockSignals(True)
        self.active_dict_combo.clear()
        current_selection_index = 0
        display_names = list(available_dict_items.keys())
        self.active_dict_combo.addItems(display_names)

        key_exists = current_selection_key in available_dict_items.values()
        if not key_exists and current_selection_key == "dic":
            self.config.set_active_dictionary("lite")
            current_selection_key = "lite"
            current_selection_index = 0
            config_changed = True
        elif key_exists:
            for i, key in enumerate(available_dict_items.values()):
                if key == current_selection_key:
                    current_selection_index = i
                    break

        self.active_dict_combo.setCurrentIndex(current_selection_index)
        self.active_dict_combo.blockSignals(False)
        self.toggle_controls()
        if config_changed:
            new_suffix = self.get_current_suffix()
            self.dictionary_changed.emit(new_suffix)

    def on_active_dict_changed(self, text):
        new_key = "lite"
        if text != "UniDic-Lite（デフォルト）":
            dic_path = self.config.get_unidic_path("dic")

            if dic_path and os.path.exists(dic_path):
                new_key = "dic"
            else:
                QMessageBox.warning(
                    self,
                    "辞書エラー",
                    f"選択された辞書 '{text}' が見つかりません。UniDic-Liteを使用します。",
                )
                self.config.set_active_dictionary("lite")
                self.update_dictionary_list()
                return

        if self.config.get_active_dictionary() != new_key:
            self.config.set_active_dictionary(new_key)
            self.toggle_controls()
            new_suffix = self.get_current_suffix()
            self.dictionary_changed.emit(new_suffix)

    def select_dictionary(self, dict_type):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "カスタム辞書設定ファイル (dicrc) を選択",
            "",
            "辞書設定ファイル (*dicrc);;全てのファイル (*.*)",
        )
        if filename:
            if not filename.lower().endswith("dicrc"):
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("ファイル形式エラー")
                msg_box.setText("dicrc ファイルを選択してください。")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec()
                return

            try:
                readme_dir = os.path.dirname(filename)
                readme_path = None
                for f in os.listdir(readme_dir):
                    if f.upper().startswith("README") and os.path.isfile(
                        os.path.join(readme_dir, f)
                    ):
                        readme_path = os.path.join(readme_dir, f)
                        break

                if not readme_path:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("エラー")
                    msg_box.setText("辞書情報を取得できませんでした。")
                    msg_box.setInformativeText(
                        "dicrcファイルと同じフォルダにREADMEファイルがあるか確認してください。"
                    )
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    self._style_message_box_buttons(msg_box)
                    msg_box.exec()
                    return

                if readme_path:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(
                            keyword in content
                            for keyword in ["上代語", "中古和文", "和歌"]
                        ):
                            msg_box = QMessageBox(self)
                            msg_box.setWindowTitle("非対応辞書")
                            msg_box.setText("このUniDicは動作対象外です。")
                            msg_box.setIcon(QMessageBox.Warning)
                            msg_box.setStandardButtons(QMessageBox.Ok)
                            self._style_message_box_buttons(msg_box)
                            msg_box.exec()
                            return
            except Exception as e:
                logging.warning(f"Could not check dictionary README: {e}")

            try:
                normalized_path = normalize_path(filename)
                self.config.set_unidic_path(dict_type, normalized_path)
                self.config.set_active_dictionary(dict_type)
                self.config.save()
                self.update_dictionary_list()
                new_suffix = self.get_current_suffix()
                self.dictionary_changed.emit(new_suffix)
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("成功")
                msg_box.setText("カスタム辞書が設定されました。")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec()
            except Exception as e:
                logging.error(f"Dictionary setting error: {e}")
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("エラー")
                msg_box.setText(f"辞書の設定に失敗しました: {str(e)}")
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec()
                self.config.set_unidic_path(dict_type, None)
                if self.config.get_active_dictionary() == dict_type:
                    self.config.set_active_dictionary("lite")
                self.update_dictionary_list()
                new_suffix = self.get_current_suffix()
                self.dictionary_changed.emit(new_suffix)

    def clear_custom_dictionary(self):
        if not self.config.get_unidic_path("dic"):
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("確認")
        msg_box.setText(
            "カスタム辞書設定をクリアしますか？\n(ユーザー辞書もクリアされます)"
        )
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        self._style_message_box_buttons(msg_box)
        reply = msg_box.exec()

        if reply == QMessageBox.Yes:
            self._calling_from_custom_clear = True
            self.clear_user_dictionary()
            self._calling_from_custom_clear = False

            self.config.set_unidic_path("dic", None)
            if self.config.get_active_dictionary() == "dic":
                self.config.set_active_dictionary("lite")
            self.config.save()
            self.update_dictionary_list()
            default_suffix = self.dictionary_info.get("lite", {}).get(
                "suffix", "_unidic-lite-1.0.8"
            )
            self.dictionary_changed.emit(default_suffix)

    def select_user_dictionary(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "ユーザー辞書ファイル (.dic) を選択",
            "",
            "辞書ファイル (*.dic);;全てのファイル (*.*)",
        )
        if filename:
            if not filename.lower().endswith(".dic"):
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("ファイル形式エラー")
                msg_box.setText(".dic ファイルを選択してください。")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec()
                return
            try:
                normalized_path = normalize_path(filename)

                is_compatible = self._check_dictionary_compatibility(normalized_path)

                if not is_compatible:

                    error_msg = QMessageBox(self)
                    error_msg.setWindowTitle("辞書互換性エラー")
                    error_msg.setText(
                        "選択されたユーザー辞書はカスタム辞書と互換性がありません"
                    )
                    error_msg.setInformativeText(
                        "登録したカスタム辞書のユーザー辞書を使用してください"
                    )
                    error_msg.setIcon(QMessageBox.Warning)
                    error_msg.setStandardButtons(QMessageBox.Ok)
                    self._style_message_box_buttons(error_msg)
                    error_msg.exec()
                    return

                self.config.set_user_dictionary_path(normalized_path)
                self.config.save()
                self.toggle_controls()
                new_suffix = self.get_current_suffix()
                self.dictionary_changed.emit(new_suffix)
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("成功")
                msg_box.setText("ユーザー辞書が設定されました。")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec()
            except Exception as e:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("エラー")
                msg_box.setText(f"ユーザー辞書の設定に失敗しました: {str(e)}")
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec()
                self.config.set_user_dictionary_path(None)
                self.toggle_controls()
                new_suffix = self.get_current_suffix()
                self.dictionary_changed.emit(new_suffix)

    def clear_user_dictionary(self):
        if (
            not self.config.get_user_dictionary_path()
            and not self._calling_from_custom_clear
        ):
            return

        if not self._calling_from_custom_clear:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("確認")
            msg_box.setText("ユーザー辞書設定をクリアしますか？")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            self._style_message_box_buttons(msg_box)
            reply = msg_box.exec()
            if reply == QMessageBox.No:
                return

        self.config.set_user_dictionary_path(None)
        self.config.save()
        self.toggle_controls()
        new_suffix = self.get_current_suffix()
        self.dictionary_changed.emit(new_suffix)

    def _style_message_box_buttons(self, msg_box):
        apply_message_box_style(msg_box)

    def _check_dictionary_compatibility(self, user_dict_path):
        try:

            active_dict = self.config.get_active_dictionary()
            dict_path = self.config.get_unidic_path(active_dict)

            if active_dict == "lite" or not dict_path:
                logging.warning("ユーザー辞書はliteでは使用できません")
                return False

            options = ""
            if dict_path and isinstance(dict_path, str) and os.path.exists(dict_path):
                if os.path.isdir(dict_path):
                    dict_path_win = dict_path.replace("/", "\\")
                    options = f'-d "{dict_path_win}"'
                elif os.path.isfile(dict_path):
                    dict_dir_win = os.path.dirname(dict_path).replace("/", "\\")
                    options = f'-d "{dict_dir_win}"'

            if not options:
                logging.warning(f"システム辞書パスが見つかりません: {dict_path}")
                return False

            user_dict_win = user_dict_path.replace("/", "\\")
            with_user_dict_options = f'{options} -u "{user_dict_win}"'

            tagger = fugashi.Tagger(with_user_dict_options)
            tagger("テスト文章です")
            return True

        except Exception as e:
            error_msg = str(e)
            logging.warning(f"辞書互換性チェックエラー: {e}")
            if "incompatible dictionary" in error_msg:
                logging.warning(f"辞書の互換性がありません: {user_dict_path}")
            return False

    def toggle_controls(self):
        config_changed = self.check_dictionary_paths()
        active_dict_key = self.config.get_active_dictionary()
        custom_dict_path = self.config.get_unidic_path("dic")
        has_custom_dict = bool(custom_dict_path and os.path.exists(custom_dict_path))
        user_dict_path = self.config.get_user_dictionary_path()
        has_user_dict = bool(user_dict_path and os.path.exists(user_dict_path))

        self.dic_entry.setText(custom_dict_path if has_custom_dict else "未設定")
        self.user_dict_entry.setText(user_dict_path if has_user_dict else "未設定")

        dic_entry_enabled = False
        dic_button_enabled = False
        dic_clear_enabled = False
        user_entry_enabled = False
        user_button_enabled = False
        user_clear_enabled = False

        if active_dict_key == "lite":
            dic_entry_enabled = False
            dic_button_enabled = True
            dic_clear_enabled = has_custom_dict
            user_entry_enabled = False
            user_button_enabled = False
            user_clear_enabled = False
        else:
            if has_custom_dict:
                dic_entry_enabled = True
                dic_button_enabled = False
                dic_clear_enabled = True
                user_entry_enabled = has_user_dict
                user_button_enabled = not has_user_dict
                user_clear_enabled = has_user_dict
            else:
                dic_entry_enabled = False
                dic_button_enabled = True
                dic_clear_enabled = False
                user_entry_enabled = False
                user_button_enabled = False
                user_clear_enabled = False

        self.dic_entry.setEnabled(dic_entry_enabled)
        self.dic_button.setEnabled(dic_button_enabled)
        self.dic_clear_button.setEnabled(dic_clear_enabled)
        self.user_dict_entry.setEnabled(user_entry_enabled)
        self.user_dict_button.setEnabled(user_button_enabled)
        self.user_dict_clear_button.setEnabled(user_clear_enabled)

        if config_changed:
            new_suffix = self.get_current_suffix()
            self.dictionary_changed.emit(new_suffix)

    def _generate_english_suffix(self, readme_content: str) -> str:
        from utils.dictionary_info import _generate_english_suffix_from_readme as gen

        return gen(readme_content)

    def _update_dictionary_info(self, dict_path):
        if not dict_path or not os.path.exists(dict_path):
            return "カスタム辞書", "unidic-custom"
        try:
            dicrc_dir = os.path.dirname(dict_path)
            readme_path = None
            for file in os.listdir(dicrc_dir):
                if file.upper().startswith("README") and os.path.isfile(
                    os.path.join(dicrc_dir, file)
                ):
                    readme_path = os.path.join(dicrc_dir, file)
                    break

            if readme_path:
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.splitlines()
                    display_name = (
                        lines[1].strip() if len(lines) >= 2 else "カスタム辞書"
                    )
                    english_suffix = self._generate_english_suffix(content)
                    return display_name, english_suffix
        except Exception as e:
            logging.error(f"Error getting dictionary info: {e}")

        return "カスタム辞書", "unidic-custom"

    def get_current_suffix(self) -> str:
        active_key = self.config.get_active_dictionary()
        base_suffix = self.dictionary_info.get(active_key, {}).get(
            "suffix", "_unidic-lite-1.0.8"
        )

        if active_key == "lite":
            return base_suffix

        user_dict_path = self.config.get_user_dictionary_path()
        if user_dict_path and os.path.exists(user_dict_path):
            return f"{base_suffix}_ud"
        return base_suffix
