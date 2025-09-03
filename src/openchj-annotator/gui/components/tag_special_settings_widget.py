import re

from gui.styles import (
    apply_button_style,
    apply_message_box_style,
    apply_tag_special_settings_style,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class TagSpecialSettingsWidget(QWidget):
    config_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tag_patterns = []
        self.max_patterns = 5
        self._setup_ui()

    def extract_strict_special_tags(self, text, tag_patterns):
        results = []

        bracket_map = {
            "square": ("\\[", "\\]"),
            "square_full": ("［", "］"),
            "round": ("\\(", "\\)"),
            "round_full": ("（", "）"),
            "curly": ("\\{", "\\}"),
            "curly_full": ("｛", "｝"),
            "angle": ("<", ">"),
            "angle_full": ("＜", "＞"),
            "corner": ("【", "】"),
        }

        for pattern in tag_patterns:
            bracket_type = pattern.get("bracket_type")
            if bracket_type not in bracket_map:
                continue
            l_b, r_b = bracket_map[bracket_type]

            tag_letter = pattern["tag_content"]
            surface = re.escape(pattern["surface_form"])

            regexes = [
                re.compile(f"{l_b}{tag_letter}{surface}{r_b}"),
                re.compile(f"{l_b}{tag_letter}:{surface}{r_b}"),
                re.compile(rf"{l_b}{tag_letter}:\s{surface}{r_b}"),
                re.compile(rf"{l_b}{tag_letter}\s{surface}{r_b}"),
            ]

            for regex in regexes:
                for match in regex.finditer(text):
                    results.append(
                        {
                            "match": match.group(),
                            "start": match.start(),
                            "end": match.end(),
                            "surface_form": pattern["surface_form"],
                            "pos_value": pattern["pos_value"],
                        }
                    )

        return results

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        input_frame = QFrame()
        apply_tag_special_settings_style(input_frame, "input_frame")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)

        tag_label = QLabel("タグ:")
        apply_tag_special_settings_style(tag_label, "label")
        tag_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.bracket_combo = QComboBox()
        apply_tag_special_settings_style(self.bracket_combo, "special_settings_combo")
        self.bracket_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.bracket_combo.setFixedWidth(70)
        self.bracket_combo.addItem("-選択-", "")
        self.bracket_combo.addItem("<>", "angle")
        self.bracket_combo.addItem("[]", "square")
        self.bracket_combo.addItem("()", "round")
        self.bracket_combo.addItem("{}", "curly")

        self.tag_content_edit = QLineEdit()
        apply_tag_special_settings_style(self.tag_content_edit, "tag_content_edit")
        self.tag_content_edit.setMaxLength(1)
        self.tag_content_edit.setFixedWidth(30)
        self.tag_content_edit.setPlaceholderText("F")

        self.surface_form_edit = QLineEdit()
        apply_tag_special_settings_style(self.surface_form_edit, "surface_form_edit")
        self.surface_form_edit.setPlaceholderText("書字形出現形")
        self.surface_form_edit.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Fixed
        )
        self.surface_form_edit.setMaximumWidth(9999)

        pos_label = QLabel("品詞:")
        apply_tag_special_settings_style(pos_label, "label")
        pos_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.pos_combo = QComboBox()
        apply_tag_special_settings_style(self.pos_combo, "special_settings_combo")
        self.pos_combo.setFixedWidth(110)
        self.pos_combo.addItem("-選択-", "")
        self.pos_combo.addItem("名詞-固有名詞", "名詞-固有名詞")
        self.pos_combo.addItem("連体詞", "連体詞")
        self.pos_combo.addItem("感動詞-フィラー", "感動詞-フィラー")

        self.add_button = QPushButton("追加")
        apply_tag_special_settings_style(self.add_button, "add_button")
        self.add_button.setFixedWidth(40)
        self.add_button.clicked.connect(self._add_pattern)

        input_layout.addWidget(tag_label)
        input_layout.addWidget(self.bracket_combo)
        input_layout.addWidget(self.tag_content_edit)
        input_layout.addWidget(self.surface_form_edit)
        input_layout.addWidget(pos_label)
        input_layout.addWidget(self.pos_combo)
        input_layout.addWidget(self.add_button)
        main_layout.addWidget(input_frame)

        self.patterns_layout = QVBoxLayout()
        self.patterns_layout.setContentsMargins(0, 5, 0, 0)
        self.patterns_layout.setSpacing(3)
        main_layout.addLayout(self.patterns_layout)
        self.setLayout(main_layout)

    def _add_pattern(self):
        bracket_type = self.bracket_combo.currentData()
        if not bracket_type:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "入力エラー",
                "括弧タイプを選択してください",
                QMessageBox.Ok,
                self,
            )
            apply_message_box_style(msg_box)
            msg_box.exec_()
            return

        tag_content = self.tag_content_edit.text().strip()
        if not tag_content:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "入力エラー",
                "タグ内容を入力してください",
                QMessageBox.Ok,
                self,
            )
            apply_message_box_style(msg_box)
            msg_box.exec_()
            return

        if not (len(tag_content) == 1 and tag_content.isalpha()):
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "入力エラー",
                "タグは半角英字1文字で入力してください\n\n例: F (フィラー用), S (特殊タグ用) など",
                QMessageBox.Ok,
                self,
            )
            apply_message_box_style(msg_box)
            msg_box.exec_()
            return

        pos_value = self.pos_combo.currentData()
        if not pos_value:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "入力エラー",
                "品詞を選択してください",
                QMessageBox.Ok,
                self,
            )
            apply_message_box_style(msg_box)
            msg_box.exec_()
            return

        if len(self.tag_patterns) >= self.max_patterns:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "上限エラー",
                f"タグパターンは最大{self.max_patterns}個までです",
                QMessageBox.Ok,
                self,
            )
            apply_message_box_style(msg_box)
            msg_box.exec_()
            return

        surface_form = self.surface_form_edit.text().strip()
        if not surface_form:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "入力エラー",
                "書字形出現形を入力してください\n\n例: 「あの」, 「えーと」 など",
                QMessageBox.Ok,
                self,
            )
            apply_message_box_style(msg_box)
            msg_box.exec_()
            return

        pattern = {
            "bracket_type": bracket_type,
            "tag_content": tag_content,
            "surface_form": surface_form,
            "pos_value": pos_value,
        }

        self.tag_patterns.append(pattern)
        self._refresh_pattern_list()

        self.tag_content_edit.clear()
        self.surface_form_edit.clear()
        self.bracket_combo.setCurrentIndex(0)
        self.pos_combo.setCurrentIndex(0)
        self.config_changed.emit()

    def _refresh_pattern_list(self):
        while self.patterns_layout.count():
            item = self.patterns_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, pattern in enumerate(self.tag_patterns):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(5)

            num_label = QLabel(f"({i+1})")
            num_label.setFixedWidth(30)
            num_label.setAlignment(Qt.AlignCenter)
            num_label.setStyleSheet("QLabel { color: #444; border: none; }")
            row_layout.addWidget(num_label)

            tag_content_example = pattern["surface_form"]
            original_tags = []

            if pattern["bracket_type"] == "angle":
                original_tags = [
                    f"<{pattern['tag_content']}{tag_content_example}>",
                    f"<{pattern['tag_content']}:{tag_content_example}>",
                    f"<{pattern['tag_content']}: {tag_content_example}>",
                    f"<{pattern['tag_content']} {tag_content_example}>",
                ]
            elif pattern["bracket_type"] == "round":
                original_tags = [
                    f"({pattern['tag_content']}{tag_content_example})",
                    f"({pattern['tag_content']}:{tag_content_example})",
                    f"({pattern['tag_content']}: {tag_content_example})",
                    f"({pattern['tag_content']} {tag_content_example})",
                ]
            elif pattern["bracket_type"] == "square":
                original_tags = [
                    f"[{pattern['tag_content']}{tag_content_example}]",
                    f"[{pattern['tag_content']}:{tag_content_example}]",
                    f"[{pattern['tag_content']}: {tag_content_example}]",
                    f"[{pattern['tag_content']} {tag_content_example}]",
                ]
            elif pattern["bracket_type"] == "curly":
                original_tags = [
                    f"{{{pattern['tag_content']}{tag_content_example}}}",
                    f"{{{pattern['tag_content']}:{tag_content_example}}}",
                    f"{{{pattern['tag_content']}: {tag_content_example}}}",
                    f"{{{pattern['tag_content']} {tag_content_example}}}",
                ]

            output_form = pattern["surface_form"]
            pattern_info = f"\"{original_tags[0]}\"　→　\"{output_form}\" ({pattern['pos_value']}) として出力"
            pattern_text = QLineEdit(pattern_info)
            pattern_text.setReadOnly(True)
            apply_tag_special_settings_style(pattern_text, "pattern_text")
            row_layout.addWidget(pattern_text)

            delete_btn = QPushButton("✕")
            apply_button_style(delete_btn, "secondary")
            apply_tag_special_settings_style(delete_btn, "delete_button")
            delete_btn.setFixedSize(20, 20)
            delete_btn.clicked.connect(lambda _, idx=i: self._delete_pattern(idx))
            row_layout.addWidget(delete_btn)
            self.patterns_layout.addWidget(row_widget)

    def _delete_pattern(self, index):
        if 0 <= index < len(self.tag_patterns):
            del self.tag_patterns[index]
            self._refresh_pattern_list()
            self.config_changed.emit()

    def clear_patterns(self):
        self.tag_patterns = []
        self._refresh_pattern_list()
        self.config_changed.emit()

    def set_config(self, config):
        if config and "tag_patterns" in config:
            self.tag_patterns = config["tag_patterns"].copy()
            self._refresh_pattern_list()

    def get_config(self):
        return {"tag_patterns": self.tag_patterns}
