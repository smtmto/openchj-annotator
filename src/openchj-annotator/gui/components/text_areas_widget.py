from typing import Dict, List, Optional

from gui.styles import (DEFAULT_FONT_FAMILY, apply_button_style,
                        apply_label_style, apply_table_scrollbar_style,
                        apply_text_areas_style)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                               QSplitter, QTableWidget, QTableWidgetItem,
                               QTextEdit, QVBoxLayout, QWidget)


class TextAreasWidget(QWidget):
    input_text_changed = Signal()
    format_settings_clicked = Signal()
    analyze_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_text_truncated = False
        self.full_input_text = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setHandleWidth(6)
        apply_text_areas_style(main_splitter, "main_splitter")
        layout.addWidget(main_splitter, 1)

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setHandleWidth(6)
        apply_text_areas_style(top_splitter, "top_splitter")
        main_splitter.addWidget(top_splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 1, 0)
        left_layout.setSpacing(3)

        input_header_layout = QHBoxLayout()
        input_label = QLabel("入力テキスト:")
        apply_label_style(input_label, "header")
        input_header_layout.addWidget(input_label)

        self.input_stats_label = QLabel("")
        apply_label_style(self.input_stats_label, "stats")

        self.input_stats_label.setWordWrap(True)
        self.input_stats_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.input_stats_label.setMinimumWidth(100)
        self.input_stats_label.setMaximumWidth(400)

        apply_text_areas_style(self.input_stats_label, "stats_label")
        input_header_layout.addWidget(self.input_stats_label, 1)
        input_header_layout.addStretch()
        left_layout.addLayout(input_header_layout)

        self.input_text = QTextEdit()
        self.input_text.setReadOnly(True)
        self.input_text.setMinimumWidth(130)
        self.input_text.setMinimumHeight(100)
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        apply_text_areas_style(self.input_text, "text_edit")
        self.input_text.textChanged.connect(self.input_text_changed.emit)
        left_layout.addWidget(self.input_text)
        top_splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(1, 0, 0, 0)
        right_layout.setSpacing(3)

        format_header_layout = QHBoxLayout()
        format_header_layout.setObjectName("format_header_layout")
        format_label = QLabel("整形テキスト:")
        apply_label_style(format_label, "header")
        format_header_layout.addWidget(format_label)

        self.format_stats_label = QLabel("")
        self.format_stats_label.setObjectName("format_stats_label")
        self.format_stats_label.setFixedHeight(20)
        self.format_stats_label.setFixedWidth(100)
        apply_text_areas_style(self.format_stats_label, "stats_label")
        format_header_layout.addWidget(self.format_stats_label)

        format_header_layout.addStretch()

        self.format_settings_button = QPushButton("整形設定")
        self.format_settings_button.setObjectName("format_settings_button")
        apply_button_style(self.format_settings_button, "primary")
        self.format_settings_button.setFixedWidth(90)
        self.format_settings_button.setEnabled(False)
        self.format_settings_button.clicked.connect(self.format_settings_clicked.emit)
        format_header_layout.addWidget(self.format_settings_button)
        right_layout.addLayout(format_header_layout)

        self.format_text = QTextEdit()
        self.format_text.setReadOnly(True)
        self.format_text.setMinimumWidth(130)
        self.format_text.setMinimumHeight(100)
        self.format_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        apply_text_areas_style(self.format_text, "text_edit")
        right_layout.addWidget(self.format_text)
        top_splitter.addWidget(right_widget)

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 1, 0, 0)
        bottom_layout.setSpacing(3)

        output_header_layout = QHBoxLayout()
        output_label = QLabel("出力テキスト:")
        apply_label_style(output_label, "header")
        output_header_layout.addWidget(output_label)

        self.output_stats_label = QLabel("")
        apply_label_style(self.output_stats_label, "stats")
        apply_text_areas_style(self.output_stats_label, "output_stats_label")
        self.output_stats_label.setWordWrap(True)
        self.output_stats_label.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Minimum
        )
        output_header_layout.addWidget(self.output_stats_label, 1)
        output_header_layout.addStretch()

        self.analyze_button = QPushButton("解析")
        apply_button_style(self.analyze_button, "primary")
        self.analyze_button.setFixedWidth(90)
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_clicked.emit)
        output_header_layout.addWidget(self.analyze_button)
        bottom_layout.addLayout(output_header_layout)

        self.processing_status_label = QLabel("")
        apply_text_areas_style(self.processing_status_label, "processing_status_label")
        self.processing_status_label.setAlignment(Qt.AlignLeft)
        self.processing_status_label.setVisible(False)
        bottom_layout.addWidget(self.processing_status_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(100)
        output_font = self.output_text.font()
        output_font.setPointSize(output_font.pointSize() - 1)
        self.output_text.setFont(output_font)

        self.output_table = QTableWidget()
        self.output_table.setColumnCount(13)
        self.output_table.setHorizontalHeaderLabels(
            [
                "ファイル名",
                "サブコーパス名",
                "開始文字位置",
                "終了文字位置",
                "文境界",
                "書字形出現形",
                "語彙素",
                "語彙素読み",
                "品詞",
                "活用型",
                "活用形",
                "発音形",
                "語種",
            ]
        )
        apply_table_scrollbar_style(self.output_table)
        self.output_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.output_table.setAlternatingRowColors(True)
        self.output_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._reset_column_widths()
        bottom_layout.addWidget(self.output_table)
        main_splitter.addWidget(bottom_widget)

        total_height = 800
        main_splitter.setSizes([int(total_height * 0.6), int(total_height * 0.4)])
        default_text_area_width = 380
        top_splitter.setSizes([default_text_area_width, default_text_area_width])

    def get_input_text(self):
        return self.input_text.toPlainText()

    def get_full_input_text(self):
        return self.full_input_text

    def set_input_text(self, text):
        self.full_input_text = ""
        self.input_text.clear()
        self.full_input_text = text
        lines = text.splitlines()
        is_truncated = len(lines) > 1000

        if is_truncated:
            display_text = "\n".join(lines[:1000])
            display_text += "\n\n=プレビューはここまでです="
            self.input_text.setPlainText(display_text)
        else:
            self.input_text.setPlainText(text)

        self.input_text_truncated = is_truncated

        import gc

        gc.collect()

    def clear_input_text(self):
        self.input_text.clear()
        self.input_text_truncated = False
        self.full_input_text = ""

    def set_format_text(self, text: str):
        self.set_format_text_with_tag_info(text, None)

    def clear_format_text(self):
        self.format_text.clear()

    def set_output_text(self, text: str):
        apply_table_scrollbar_style(self.output_table)
        font = QFont(DEFAULT_FONT_FAMILY, 9)
        lines = text.strip().split("\n")
        filtered_lines = []
        is_truncated = False

        for line in lines:
            if (
                line.strip()
                and not line.startswith("ファイル名")
                and not line.startswith("===")
                and not line.startswith("---")
            ):
                filtered_lines.append(line)
                if len(filtered_lines) >= 1000:
                    is_truncated = True
                    break

        if is_truncated:
            filtered_lines.append("=プレビューはここまでです=")

        headers = [
            "ファイル名",
            "サブコーパス名",
            "開始文字位置",
            "終了文字位置",
            "文境界",
            "書字形出現形",
            "語彙素",
            "語彙素読み",
            "品詞",
            "活用型",
            "活用形",
            "発音形",
            "語種",
        ]
        self.output_table.setColumnCount(len(headers))
        self.output_table.setHorizontalHeaderLabels(headers)
        self.output_table.verticalHeader().setVisible(False)
        self.output_table.setRowCount(len(filtered_lines))

        for row_idx, line in enumerate(filtered_lines):
            columns = line.split("\t")[:13]

            self.output_table.setRowHeight(row_idx, 20)

            for col_idx, value in enumerate(columns):
                item = QTableWidgetItem(value)

                if col_idx in [2, 3]:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                elif col_idx == 4:
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                item.setFont(font)
                self.output_table.setItem(row_idx, col_idx, item)

        self.output_table.resizeColumnsToContents()

    def clear_output_text(self):
        self.output_text.clear()
        self.output_table.setRowCount(0)
        self.output_table.setHorizontalHeaderLabels(
            [
                "ファイル名",
                "サブコーパス名",
                "開始文字位置",
                "終了文字位置",
                "文境界",
                "書字形出現形",
                "語彙素",
                "語彙素読み",
                "品詞",
                "活用型",
                "活用形",
                "発音形",
                "語種",
            ]
        )

        self._reset_column_widths()

    def set_input_stats(self, text):
        self.input_stats_label.setText(text)

    def set_format_stats(self, text):
        if text:
            self.format_stats_label.setText(text)
            self.format_stats_label.setVisible(True)
        else:
            self.format_stats_label.setText("")
            self.format_stats_label.setVisible(False)

    def set_output_stats(self, text):
        self.output_stats_label.setText(text)

    def set_format_settings_button_enabled(self, enabled):
        self.format_settings_button.setEnabled(enabled)

    def set_format_text_with_tag_info(
        self,
        text_to_display: str,
        detected_special_tags: Optional[List[Dict]] = None,
    ):

        self.format_text.clear()
        cursor = self.format_text.textCursor()

        default_format = QTextCharFormat()
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(224, 240, 224))

        max_preview_lines = 1000

        if not detected_special_tags or not text_to_display.strip():

            lines = text_to_display.splitlines()
            display_text_final = text_to_display
            if len(lines) > max_preview_lines:
                display_text_final = (
                    "\n".join(lines[:max_preview_lines])
                    + "\n\n=プレビューはここまでです="
                )
                if hasattr(self, "set_format_stats"):
                    self.set_format_stats("(一部表示)")
            else:
                if hasattr(self, "set_format_stats"):
                    self.set_format_stats("")

            cursor.insertText(display_text_final, default_format)
            self.format_text.moveCursor(QTextCursor.Start)
            return

        valid_tags = [
            tag
            for tag in detected_special_tags
            if "original_char_start" in tag
            and "original_char_end" in tag
            and "surface_form" in tag
        ]
        sorted_tags = sorted(valid_tags, key=lambda tag: tag["original_char_start"])

        current_pos_in_original = 0

        inserted_line_count_total = 0

        final_text_to_insert_parts = []

        for tag_info in sorted_tags:
            orig_start = tag_info["original_char_start"]
            orig_end = tag_info["original_char_end"]
            surface_to_display_for_tag = tag_info["surface_form"]

            if orig_start > current_pos_in_original:
                segment_before = text_to_display[current_pos_in_original:orig_start]
                final_text_to_insert_parts.append((segment_before, default_format))

            final_text_to_insert_parts.append(
                (surface_to_display_for_tag, highlight_format)
            )

            current_pos_in_original = orig_end

        if current_pos_in_original < len(text_to_display):
            final_text_to_insert_parts.append(
                (text_to_display[current_pos_in_original:], default_format)
            )

        for text_segment, char_format_to_apply in final_text_to_insert_parts:
            if inserted_line_count_total >= max_preview_lines:
                break

            segment_lines = text_segment.splitlines(keepends=True)
            for i, line_part in enumerate(segment_lines):
                if inserted_line_count_total >= max_preview_lines:
                    break

                cursor.insertText(line_part, char_format_to_apply)

                if (
                    i < len(segment_lines) - 1
                    and line_part.endswith(("\n", "\r\n", "\r"))
                ) or (
                    len(segment_lines) == 1
                    and text_segment.endswith(("\n", "\r\n", "\r"))
                ):
                    inserted_line_count_total += 1

        if inserted_line_count_total >= max_preview_lines:
            current_text_in_editor = self.format_text.toPlainText()

            if not current_text_in_editor.endswith("\n\n=プレビューはここまでです="):
                if current_text_in_editor.endswith("\n"):
                    cursor.insertText("\n=プレビューはここまでです=", default_format)
                else:
                    cursor.insertText("\n\n=プレビューはここまでです=", default_format)
            if hasattr(self, "set_format_stats"):
                self.set_format_stats("(一部表示)")
        else:
            if hasattr(self, "set_format_stats"):
                self.set_format_stats("")

        self.format_text.moveCursor(QTextCursor.Start)

    def set_analyze_button_enabled(self, enabled):
        self.analyze_button.setEnabled(enabled)

    def clear_all_texts(self):
        self.clear_input_text()
        self.clear_format_text()
        self.clear_output_text()
        self.set_input_stats("")
        self.set_output_stats("")

        self.input_stats_label.setText("")
        self.format_stats_label.setText("")
        self.format_stats_label.setVisible(False)
        self.output_stats_label.setText("")

        self.processing_status_label.setVisible(False)

    def append_format_text(self, text: str):
        self.format_text.moveCursor(QTextCursor.End)
        self.format_text.insertPlainText(text)
        self.format_text.moveCursor(QTextCursor.Start)

    def _reset_column_widths(self):
        default_widths = {
            0: 70,  # ファイル名
            1: 90,  # サブコーパス名
            2: 90,  # 開始文字位置
            3: 90,  # 終了文字位置
            4: 50,  # 文境界
            5: 90,  # 書字形出現形
            6: 50,  # 語彙素
            7: 80,  # 語彙素読み
            8: 40,  # 品詞
            9: 50,  # 活用型
            10: 50,  # 活用形
            11: 50,  # 発音形
            12: 40,  # 語種
        }

        for col, width in default_widths.items():
            if col < self.output_table.columnCount():
                self.output_table.setColumnWidth(col, width)

    def update_processing_status(self, is_processing: bool, message: str = ""):
        if is_processing:
            self.processing_status_label.setText(message or "処理中...")
            self.processing_status_label.setVisible(True)
        else:
            self.processing_status_label.setVisible(False)
