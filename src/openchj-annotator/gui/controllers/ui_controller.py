import logging
import os
import platform
import subprocess
from typing import Dict, Optional

from gui.dialogs.format_settings.format_settings_dialog import FormatSettingsDialog
from gui.dialogs.show_custom_dict_help import show_custom_dict_help_dialog
from gui.dialogs.show_user_dict_help import show_user_dict_help_dialog
from gui.styles import apply_button_style
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox
from utils.path_manager import get_resource_path


class UIController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.config = main_window.config
        self.preview_timer = None

    def handle_input_text_changed(self):
        self.update_preview()
        self.update_analyze_button_state()
        has_text = bool(self.main_window.analyze_tab.get_input_text().strip())
        self.main_window.analyze_tab.set_clear_button_enabled(has_text)

    def update_analyze_button_state(self):
        has_text = bool(self.main_window.analyze_tab.get_input_text().strip())
        self.main_window.analyze_tab.set_analyze_button_enabled(
            has_text and self.main_window.analyzer is not None
        )

    def update_preview(self):
        if hasattr(self, "preview_timer") and self.preview_timer is not None:
            self.preview_timer.stop()
            self.preview_timer.deleteLater()
            self.preview_timer = None

        QTimer.singleShot(10, self._create_preview_timer)

    def _update_preview_now(self, temp_format_settings: Optional[Dict] = None):
        if not self.main_window.analyze_tab:
            logging.warning(
                "_update_preview_now: self.main_window.analyze_tab is None. Skipping preview."
            )
            return
        if not self.main_window.analyzer:
            logging.warning(
                "_update_preview_now: self.main_window.analyzer is None. Skipping preview."
            )
            return

        input_text = self.main_window.analyze_tab.get_input_text()

        if not input_text or not input_text.strip():
            self.main_window.analyze_tab.set_format_text_with_tag_info("", None)
            return

        try:

            text_for_display, detected_tags_for_highlight = (
                self.main_window.analyzer.preprocess_text_with_tag_info(
                    input_text, temp_format_settings=temp_format_settings
                )
            )

            self.main_window.analyze_tab.set_format_text_with_tag_info(
                text_for_display,
                final_adjusted_tags=detected_tags_for_highlight,
            )

        except Exception as e:
            import traceback

            logging.error(f"_update_preview_now: Preview update error: {e}")
            logging.error(traceback.format_exc())
            error_msg = f"プレビュー表示エラー: {str(e)}"
            try:

                self.main_window.analyze_tab.set_format_text_with_tag_info(
                    error_msg, None
                )

                text_areas_widget_instance = (
                    self.main_window.analyze_tab.text_areas_widget
                )
                if hasattr(text_areas_widget_instance, "format_stats_label"):
                    text_areas_widget_instance.format_stats_label.setText("")
                    text_areas_widget_instance.format_stats_label.setVisible(False)
            except Exception as inner_e:
                logging.error(
                    f"_update_preview_now: Failed to set error message in format_text: {inner_e}"
                )

        if self.preview_timer:
            self.preview_timer = None

    def _create_preview_timer(self):
        self.preview_timer = QTimer(self.main_window)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(
            lambda: self._update_preview_now(temp_format_settings=None)
        )
        self.preview_timer.start(500)

    def handle_selection_cleared(self):
        analyze_tab = self.main_window.analyze_tab
        analyze_tab.text_areas_widget.clear_all_texts()
        analyze_tab.set_analyze_button_enabled(False)
        analyze_tab.set_download_button_enabled(False)
        analyze_tab.set_format_settings_button_enabled(False)
        analyze_tab.set_clear_button_enabled(False)
        analyze_tab.update_processing_status(False, "")

        self.main_window.current_result_text = None
        self.main_window.current_result_data = None

    def show_format_settings(self):
        dialog = FormatSettingsDialog(self.main_window)
        dialog.settings_applied.connect(self._handle_format_settings_applied)
        dialog.exec_()

    def _handle_format_settings_applied(self, new_settings):
        self._update_preview_now(temp_format_settings=new_settings)

    def show_user_dict_help(self):
        try:
            help_file = get_resource_path("help", "user_dictionary_help.html")
            if not help_file.exists():
                logging.error(f"User dictionary help file not found at {help_file}")
                QMessageBox.warning(
                    self.main_window,
                    "エラー",
                    f"ヘルプファイルが見つかりません:\n{help_file}",
                )
                return
            show_user_dict_help_dialog(self.main_window, str(help_file))
        except Exception as e:
            logging.error(f"Error showing user dict help: {e}")
            QMessageBox.critical(
                self.main_window, "エラー", f"ヘルプ表示中にエラーが発生しました:\n{e}"
            )

    def show_custom_dict_help(self):
        try:
            help_file = get_resource_path("help", "custom_dictionary_help.html")
            if not help_file.exists():
                logging.error(f"Custom dictionary help file not found at {help_file}")
                QMessageBox.warning(
                    self.main_window,
                    "エラー",
                    f"ヘルプファイルが見つかりません:\n{help_file}",
                )
                return
            show_custom_dict_help_dialog(self.main_window, str(help_file))
        except Exception as e:
            logging.error(f"Error showing custom dict help: {e}")
            QMessageBox.critical(
                self.main_window, "エラー", f"ヘルプ表示中にエラーが発生しました:\n{e}"
            )

    def open_folder_or_select_file(self, path, select=False):
        try:
            if not os.path.exists(path):
                QMessageBox.warning(
                    self.main_window, "エラー", f"パスが見つかりません: {path}"
                )
                return
            system = platform.system()
            if system == "Windows":
                if os.path.isdir(path):
                    subprocess.run(
                        ["explorer", path],
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                elif os.path.isfile(path):
                    if select:
                        subprocess.run(
                            ["explorer", "/select,", path],
                            check=True,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                        )
                    else:
                        os.startfile(path)
            elif system == "Darwin":
                if os.path.isdir(path):
                    subprocess.run(["open", path], check=True)
                elif os.path.isfile(path):
                    subprocess.run(["open", "-R", path], check=True)
            else:
                if os.path.isdir(path):
                    subprocess.run(["xdg-open", path], check=True)
                elif os.path.isfile(path):
                    subprocess.run(["xdg-open", path], check=True)
        except Exception as e:
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("エラー")
            msg_box.setText(f"ファイル/フォルダを開けませんでした: {e}")
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setStandardButtons(QMessageBox.Ok)
            self._style_message_box_buttons(msg_box)
            msg_box.exec_()

    def _style_message_box_buttons(self, msg_box):
        for button in msg_box.buttons():
            apply_button_style(button, "default")
