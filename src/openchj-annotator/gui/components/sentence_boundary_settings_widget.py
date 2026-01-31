from typing import Optional

from gui.custom_widgets import CustomCheckBox
from gui.styles import apply_checkbox_style, apply_combobox_style, apply_label_style
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from config import Config

DEFAULT_BOUNDARY_SETTINGS = {
    "end_punct": "。",
    "end_quote": "設定なし",
    "use_explicit_marker": False,
}


class SentenceBoundarySettingsWidget(QWidget):
    def __init__(self, parent=None, config: Optional[Config] = None):
        super().__init__(parent)
        self.config = config
        self._loading_settings = False
        self._setup_ui()
        self._connect_signals()
        self.load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        group = QGroupBox("文境界設定")
        group.setMinimumHeight(80)
        grid = QGridLayout(group)
        grid.setContentsMargins(10, 6, 10, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(0)

        end_punct_label = QLabel("次の記号を文末に設定する")
        apply_label_style(end_punct_label)
        end_punct_label.setFixedWidth(135)
        grid.addWidget(end_punct_label, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        self.end_punct_combo = QComboBox()
        self.end_punct_combo.addItems(["。", "。, ？", "。, ？, ！", "設定なし"])
        apply_combobox_style(self.end_punct_combo)
        self.end_punct_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.end_punct_combo.setMinimumWidth(100)
        self.end_punct_combo.setFixedHeight(22)
        grid.addWidget(self.end_punct_combo, 0, 1, Qt.AlignLeft | Qt.AlignVCenter)

        grid.addItem(QSpacerItem(30, 0, QSizePolicy.Fixed, QSizePolicy.Minimum), 0, 2)

        end_quote_label = QLabel("次の括弧を文末に設定する")
        apply_label_style(end_quote_label)
        end_quote_label.setFixedWidth(135)
        grid.addWidget(end_quote_label, 0, 3, Qt.AlignLeft | Qt.AlignVCenter)

        self.end_quote_combo = QComboBox()
        self.end_quote_combo.addItems(["」", "』", "」, 』", "設定なし"])
        apply_combobox_style(self.end_quote_combo)
        self.end_quote_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.end_quote_combo.setMinimumWidth(90)
        self.end_quote_combo.setFixedHeight(22)
        grid.addWidget(self.end_quote_combo, 0, 4, Qt.AlignLeft | Qt.AlignVCenter)

        grid.addItem(QSpacerItem(30, 0, QSizePolicy.Fixed, QSizePolicy.Minimum), 0, 5)

        self.explicit_marker_checkbox = CustomCheckBox(
            "タグ[B]を文境界とする（出力時に[B]を削除）"
        )
        apply_checkbox_style(self.explicit_marker_checkbox, "smaller_font")
        grid.addWidget(
            self.explicit_marker_checkbox,
            0,
            6,
            1,
            1,
            Qt.AlignLeft | Qt.AlignVCenter,
        )
        grid.setColumnStretch(6, 1)

        layout.addWidget(group)

    def _connect_signals(self):
        self.end_punct_combo.currentTextChanged.connect(self._on_settings_changed)
        self.end_quote_combo.currentTextChanged.connect(self._on_settings_changed)
        self.explicit_marker_checkbox.stateChanged.connect(self._on_settings_changed)

    def _on_settings_changed(self):
        if self._loading_settings or not self.config:
            return

        settings = self.config.config.get("sentence_boundary_settings", {}).copy()
        settings.update(
            {
                "end_punct": self.end_punct_combo.currentText(),
                "end_quote": self.end_quote_combo.currentText(),
                "use_explicit_marker": self.explicit_marker_checkbox.isChecked(),
            }
        )
        self.config.config["sentence_boundary_settings"] = settings
        self.config.save()

    def load_settings(self):
        if not self.config:
            return

        self._loading_settings = True
        try:
            settings = self.config.config.get(
                "sentence_boundary_settings", DEFAULT_BOUNDARY_SETTINGS.copy()
            )

            end_punct = settings.get(
                "end_punct", DEFAULT_BOUNDARY_SETTINGS["end_punct"]
            )
            end_quote = settings.get(
                "end_quote", DEFAULT_BOUNDARY_SETTINGS["end_quote"]
            )
            use_marker = settings.get(
                "use_explicit_marker",
                DEFAULT_BOUNDARY_SETTINGS["use_explicit_marker"],
            )

            if self.end_punct_combo.findText(end_punct) == -1:
                end_punct = DEFAULT_BOUNDARY_SETTINGS["end_punct"]
            if self.end_quote_combo.findText(end_quote) == -1:
                end_quote = DEFAULT_BOUNDARY_SETTINGS["end_quote"]

            self.end_punct_combo.setCurrentText(end_punct)
            self.end_quote_combo.setCurrentText(end_quote)
            self.explicit_marker_checkbox.setChecked(bool(use_marker))
        finally:
            self._loading_settings = False
