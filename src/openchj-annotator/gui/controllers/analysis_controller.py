import logging
import os

from gui.styles import apply_button_style
from gui.workers.analysis_worker import AnalysisWorker
from gui.workers.batch_analysis_worker import BatchAnalysisWorker
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox
from utils.file_utils import (get_downloads_directory, get_files_in_directory,
                              read_text_file, replace_datetime_placeholder)


class AnalysisController:
    def __init__(self, main_window):
        self.main_window = main_window

    def handle_file_selected(self, filenames):
        if not filenames:
            return

        if hasattr(self.main_window, "current_result_text"):
            self.main_window.current_result_text = None
        if hasattr(self.main_window, "complete_result_text"):
            self.main_window.complete_result_text = None
        if hasattr(self.main_window, "current_result_data"):
            self.main_window.current_result_data = None

    def handle_folder_selected(self, folder_path):
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(
                self.main_window, "エラー", "有効なフォルダパスが指定されていません。"
            )
            return

        if hasattr(self.main_window, "current_result_text"):
            self.main_window.current_result_text = None
        if hasattr(self.main_window, "complete_result_text"):
            self.main_window.complete_result_text = None
        if hasattr(self.main_window, "current_result_data"):
            self.main_window.current_result_data = None

        try:
            if hasattr(self.main_window.config, "config") and isinstance(
                self.main_window.config.config, dict
            ):
                output_settings = self.main_window.config.config.get(
                    "output_settings", {}
                )
                if output_settings is None:
                    logging.warning(
                        "output_settings key not found in config or is None. Using default for include_subfolders."
                    )
                    output_settings = {}
            else:
                logging.warning(
                    "Config object does not have 'config' attribute or it's not a dict. Using default for include_subfolders."
                )
                output_settings = {}

            include_subfolders = output_settings.get("include_subfolders", False)

            txt_files = []
            total_size = 0

            if include_subfolders:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        if file.lower().endswith(".txt"):
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                txt_files.append((file_path, file_size))
                                total_size += file_size
                            except OSError:
                                continue
            else:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isfile(item_path) and item.lower().endswith(".txt"):
                        try:
                            file_size = os.path.getsize(item_path)
                            txt_files.append((item_path, file_size))
                            total_size += file_size
                        except OSError:
                            continue

            if not txt_files:
                logging.warning(f"No text files found in: {folder_path}")
                self.main_window.analyze_tab.set_input_path_display(folder_path)
                QMessageBox.information(
                    self.main_window,
                    "情報",
                    "選択されたフォルダ内にテキストファイル（.txt）が見つかりませんでした。",
                )
                return

            if len(txt_files) > 50:
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("ファイル数制限エラー")
                msg_box.setText(
                    f"フォルダ内のテキストファイル数: {len(txt_files)}件\n\n"
                    f"一度に処理できるファイルは50件までです。"
                )
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec_()
                self.main_window.analyze_tab.set_input_path_display("")
                return

            if total_size > 10 * 1024 * 1024:
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("ファイルサイズ制限エラー")
                msg_box.setText(
                    f"フォルダ内のファイルの合計サイズ: {total_size / 1024 / 1024:.1f}MB\n\n"
                    f"一度に処理できるファイルの合計サイズは10MBまでです。"
                )
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec_()
                self.main_window.analyze_tab.set_input_path_display("")
                return

            txt_file_paths = [f[0] for f in txt_files]

            if len(txt_file_paths) > 0 and self.main_window.analyze_tab:
                try:
                    from utils.file_utils import read_text_file

                    content = read_text_file(txt_file_paths[0])
                    self.main_window.analyze_tab.set_input_text(content)
                    if self.main_window.ui_controller:
                        self.main_window.ui_controller.update_preview()
                except Exception as e:
                    logging.error(f"Error occurred while reading first file: {e}")

            if self.main_window.analyze_tab:
                QTimer.singleShot(
                    0,
                    lambda: self._update_ui_after_folder_selection(
                        folder_path, txt_file_paths
                    ),
                )
            else:
                logging.error("Main window's analyze_tab does not exist")

        except Exception as e:
            logging.error(f"Error occurred while processing folder selection: {e}")
            QMessageBox.critical(
                self.main_window,
                "エラー",
                f"フォルダ処理中にエラーが発生しました: {str(e)}",
            )

    def _update_ui_after_folder_selection(self, folder_path, txt_files):
        try:
            if not hasattr(self, "current_files_to_process"):
                self.current_files_to_process = []
            self.current_files_to_process = txt_files

            if self.main_window.analyze_tab:
                display_text = folder_path
                self.main_window.analyze_tab.set_input_path_display(display_text)

                info_text = f"{os.path.basename(folder_path)} (読み込まれたファイル{len(txt_files)}件のうち1件目を表示)"

                if (
                    hasattr(
                        self.main_window.analyze_tab.text_areas_widget,
                        "input_text_truncated",
                    )
                    and self.main_window.analyze_tab.text_areas_widget.input_text_truncated
                ):
                    info_text += " (一部表示)"

                self.main_window.analyze_tab.set_input_stats(info_text)

                self.main_window.repaint()

                if len(txt_files) > 0:
                    try:
                        from utils.file_utils import read_text_file

                        content = read_text_file(txt_files[0])

                        self.main_window.analyze_tab.set_input_text(content)

                        if self.main_window.ui_controller:
                            self.main_window.ui_controller.update_preview()
                    except Exception as e:
                        logging.error(f"Error occurred while reading first file: {e}")

            if self.main_window.ui_controller:
                self.main_window.ui_controller.update_analyze_button_state()

            if self.main_window.analyze_tab:
                self.main_window.analyze_tab.set_format_settings_button_enabled(True)
                has_text_in_input_area = bool(
                    self.main_window.analyze_tab.get_input_text().strip()
                )
                if len(txt_files) > 0 or has_text_in_input_area:
                    self.main_window.analyze_tab.set_clear_button_enabled(True)

        except Exception as e:
            import traceback

            logging.error(f"Error occurred while updating UI: {e}")
            logging.error(traceback.format_exc())
            try:
                QMessageBox.critical(
                    self.main_window,
                    "UI更新エラー",
                    f"UIの更新中にエラーが発生しました: {str(e)}",
                )
            except Exception:
                logging.error("Failed to display error")

    def load_preview(self, file_path):
        if not self.main_window or not self.main_window.analyze_tab:
            return
        try:
            if not os.path.exists(file_path):
                QMessageBox.warning(
                    self.main_window,
                    "エラー",
                    f"指定されたファイルが見つかりません: {file_path}",
                )
                self.main_window.analyze_tab.set_input_text(
                    f"エラー: ファイルが見つかりません - {file_path}"
                )
                return

            try:
                content = read_text_file(file_path)
            except Exception as e:
                logging.error(f"ファイル読み込みエラー: {e}")
                QMessageBox.warning(
                    self.main_window,
                    "ファイル読み込みエラー",
                    f"ファイルの読み込み中にエラーが発生しました: {str(e)}",
                )
                content = f"エラー: ファイルを読み込めませんでした: {str(e)}"
                try:
                    with open(file_path, "rb") as f:
                        binary_content = f.read()
                        content = binary_content.decode("utf-8", errors="replace")
                except Exception as fallback_error:
                    logging.error(f"Fallback read failed: {fallback_error}")
                    content = "エラー: ファイル読み込みに失敗しました。"

            self.main_window.analyze_tab.set_input_text(content)

            if self.main_window.ui_controller:
                self.main_window.ui_controller.update_preview()
                self.main_window.ui_controller.update_analyze_button_state()

            self.main_window.analyze_tab.set_format_settings_button_enabled(True)
            self.main_window.analyze_tab.set_clear_button_enabled(True)

            file_count = 1
            if hasattr(
                self.main_window.analyze_tab.file_selection_widget, "batch_files"
            ):
                batch_files = (
                    self.main_window.analyze_tab.file_selection_widget.batch_files
                )
                if batch_files and len(batch_files) > 0:
                    file_count = len(batch_files)

            stats_text = f"{os.path.basename(file_path)} (読み込まれたファイル{file_count}件のうち1件目を表示)"

            if (
                hasattr(
                    self.main_window.analyze_tab.text_areas_widget,
                    "input_text_truncated",
                )
                and self.main_window.analyze_tab.text_areas_widget.input_text_truncated
            ):
                stats_text += " (一部表示)"

            self.main_window.analyze_tab.set_input_stats(stats_text)

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "プレビューエラー",
                f"ファイルのプレビュー表示中にエラーが発生しました: {str(e)}",
            )
            if self.main_window.analyze_tab:
                self.main_window.analyze_tab.set_input_text(
                    f"エラー: {os.path.basename(file_path)} をプレビューできませんでした。"
                )

    def start_analysis(self):
        try:
            self.main_window.initialize_analyzer()
        except Exception as e:
            QMessageBox.warning(
                self.main_window,
                "エラー",
                f"アナライザーの初期化に失敗しました: {str(e)}",
            )
            return

        if not self.main_window.analyzer:
            QMessageBox.warning(
                self.main_window,
                "エラー",
                "アナライザーが初期化されていません。設定を確認してください。",
            )
            return
        if self.main_window.analyze_tab.is_batch():
            self.start_batch_analysis()
        else:
            self.start_single_analysis()

    def start_batch_analysis(self):
        files_to_process = []
        is_folder = False
        folder_path = None

        if self.main_window.analyze_tab.get_selected_folder():
            folder_path = self.main_window.analyze_tab.get_selected_folder()
            is_folder = True
            include_subfolders = self.main_window.config.config.get(
                "output_settings", {}
            ).get("include_subfolders", False)
            try:
                files_to_process = get_files_in_directory(
                    folder_path, ".txt", include_subfolders
                )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window,
                    "エラー",
                    f"フォルダ処理中にエラーが発生しました: {e}",
                )
                return
        elif self.main_window.analyze_tab.get_selected_files():
            files_to_process = self.main_window.analyze_tab.get_selected_files()
        else:
            QMessageBox.warning(
                self.main_window,
                "",
                "解析対象のファイルまたはフォルダが選択されていません。",
            )
            return

        if not files_to_process:
            QMessageBox.warning(
                self.main_window,
                "",
                "選択されたフォルダ内に解析対象のテキストファイルが見つかりません。",
            )
            return

        self.main_window.analyze_tab.processing_status_changed.emit(
            True, "バッチ処理中..."
        )
        self.main_window.batch_worker = BatchAnalysisWorker(
            self.main_window.analyzer,
            files_to_process,
            self.main_window.config,
            is_folder,
            folder_path,
        )
        self.main_window.batch_worker.message.connect(
            lambda msg: self.update_processing_message(msg)
        )
        self.main_window.batch_worker.finished.connect(self.batch_analysis_finished)
        self.main_window.batch_worker.error.connect(self.batch_analysis_error)
        self.main_window.batch_worker.start()

    def start_single_analysis(self):
        input_source = self.main_window.analyze_tab.get_input_path_display()

        if input_source and os.path.isfile(input_source):
            try:
                text = read_text_file(input_source)
                if not text.strip():
                    QMessageBox.warning(
                        self.main_window, "", "選択されたファイルは空です。"
                    )
                    return
                text_source = input_source
            except Exception as e:
                QMessageBox.warning(
                    self.main_window, "", f"ファイルの読み込みに失敗しました: {str(e)}"
                )
                return
        else:
            text = self.main_window.analyze_tab.text_areas_widget.get_full_input_text()
            if not text.strip():
                text = self.main_window.analyze_tab.get_input_text()
                if not text.strip():
                    QMessageBox.warning(
                        self.main_window, "", "解析するテキストがありません。"
                    )
                    return
            text_source = None

        self.main_window.analyze_tab.processing_status_changed.emit(True, "解析中...")
        self.main_window.worker = AnalysisWorker(
            self.main_window.analyzer, text, text_source
        )
        self.main_window.worker.message.connect(
            lambda msg: self.update_processing_message(msg)
        )
        self.main_window.worker.finished.connect(self.analysis_finished)
        self.main_window.worker.error.connect(self.analysis_error)
        self.main_window.worker.start()

    def update_processing_message(self, message):
        self.main_window.analyze_tab.processing_status_changed.emit(True, message)

    def batch_analysis_finished(self, results):
        self.main_window.analyze_tab.processing_status_changed.emit(
            True, "バッチ処理が完了しました"
        )

        QTimer.singleShot(
            800,
            lambda: self.main_window.analyze_tab.processing_status_changed.emit(
                False, ""
            ),
        )
        success_count = sum(1 for r in results if r[1])
        fail_count = len(results) - success_count
        output_dir = None
        output_settings = self.main_window.config.config.get("output_settings", {})
        is_folder_processing = (
            self.main_window.analyze_tab.get_selected_folder() is not None
        )
        selected_folder_path = self.main_window.analyze_tab.get_selected_folder()

        prefix = output_settings.get("prefix", "")
        suffix = output_settings.get("suffix", "_analyzed") or "_analyzed"
        suffix = replace_datetime_placeholder(suffix)

        if output_settings.get("use_custom_output_dir", False):
            output_dir = output_settings.get("output_directory")
            if is_folder_processing and selected_folder_path:
                folder_name = os.path.basename(selected_folder_path)
                output_dir = os.path.join(output_dir, f"{prefix}{folder_name}{suffix}")
        else:
            default_dir = (
                output_settings.get("default_directory", "")
                or get_downloads_directory()
            )
            if is_folder_processing and selected_folder_path:
                folder_name = os.path.basename(selected_folder_path)
                output_dir = os.path.join(default_dir, f"{prefix}{folder_name}{suffix}")
            else:
                output_dir = default_dir

        output_results_display = []
        max_lines = 1000
        current_lines = 0
        for filename, success, result_path_or_error in results:
            if success and result_path_or_error:
                try:
                    with open(result_path_or_error, "r", encoding="utf-8") as f:
                        for line in f:
                            if current_lines >= max_lines:
                                break
                            if line.strip() and not line.startswith("ファイル名"):
                                output_results_display.append(line.rstrip("\n"))
                                current_lines += 1
                except Exception as e:
                    if current_lines < max_lines:
                        output_results_display.append(
                            f"結果ファイルの読み込みエラー: {str(e)}"
                        )
                        current_lines += 1
            elif not success:
                if current_lines < max_lines:
                    error_lines = str(result_path_or_error).split("\n")
                    for line in error_lines:
                        if current_lines >= max_lines:
                            break
                        if line.strip():
                            output_results_display.append(line)
                            current_lines += 1

        result_text = "\n".join(output_results_display)

        self.main_window.analyze_tab.set_output_text(result_text)

        self.main_window.current_result_text = result_text

        self.main_window.complete_result_text = None
        self.main_window.current_result_data = results
        dictionary_name = (
            self.main_window.analyzer.get_current_dictionary_name()
            if self.main_window.analyzer
            else "不明"
        )
        stats_text = f"処理成功ファイル数:{success_count}　適用辞書: {dictionary_name}"
        if fail_count > 0:
            stats_text += f" (処理失敗ファイル数:{fail_count})"

        if current_lines >= max_lines or any(
            len(open(r[2], "r", encoding="utf-8").readlines()) > max_lines
            for r in results
            if r[1] and r[2]
        ):
            stats_text += " (一部表示)"

        self.main_window.analyze_tab.set_output_stats(stats_text)

        if current_lines >= max_lines:
            output_results_display.append("\n===プレビューはここまでです===")

        message = f"処理が完了しました。\n\n成功: {success_count}ファイル"
        if fail_count > 0:
            message += f"\n失敗: {fail_count}ファイル"

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("処理完了")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        self._style_message_box_buttons(msg_box)
        msg_box.exec_()

        self.main_window.analyze_tab.set_download_button_enabled(True)

    def batch_analysis_error(self, error_message):
        self.main_window.analyze_tab.processing_status_changed.emit(False, "")
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("バッチ処理エラー")
        msg_box.setText(f"バッチ処理中にエラーが発生しました: {error_message}")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        self._style_message_box_buttons(msg_box)
        msg_box.exec_()
        self.main_window.analyze_tab.set_output_text(
            f"バッチ処理エラー:\n{error_message}"
        )
        self.main_window.analyze_tab.set_output_stats("エラー発生")

    def analysis_finished(self, result_text, results):

        self.main_window.analyze_tab.processing_status_changed.emit(
            True, "処理完了しました"
        )

        QTimer.singleShot(
            800,
            lambda: self.main_window.analyze_tab.processing_status_changed.emit(
                False, ""
            ),
        )

        self.main_window.complete_result_text = result_text

        self.main_window.current_result_text = result_text

        self.main_window.current_result_data = results

        self.main_window.analyze_tab.set_output_text(result_text)

        dictionary_name = (
            self.main_window.analyzer.get_current_dictionary_name()
            if self.main_window.analyzer
            else "不明"
        )
        input_source = self.main_window.analyze_tab.get_input_path_display()
        source_name = (
            os.path.basename(input_source)
            if input_source and os.path.isfile(input_source)
            else "テキスト入力"
        )

        line_count = len(result_text.strip().splitlines())
        stats_text = f"処理成功: {source_name}　適用辞書: {dictionary_name}"

        if line_count > 1000:
            stats_text += " (一部表示)"

        self.main_window.analyze_tab.set_output_stats(stats_text)
        self.main_window.analyze_tab.set_download_button_enabled(True)

    def analysis_error(self, error_message):
        self.main_window.analyze_tab.processing_status_changed.emit(False, "")
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("解析エラー")
        msg_box.setText(f"解析に失敗しました: {error_message}")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        self._style_message_box_buttons(msg_box)
        msg_box.exec_()
        self.main_window.analyze_tab.set_output_text(f"解析エラー:\n{error_message}")
        self.main_window.analyze_tab.set_output_stats("エラー発生")
        self.main_window.analyze_tab.set_download_button_enabled(False)

    def download_result(self):
        if (
            not self.main_window.current_result_text
            and not self.main_window.current_result_data
        ):
            QMessageBox.warning(
                self.main_window, "", "ダウンロードする解析結果がありません。"
            )
            return

        output_settings = self.main_window.config.config.get("output_settings", {})
        prefix = output_settings.get("prefix", "")
        suffix = output_settings.get("suffix", "_analyzed") or "_analyzed"
        suffix = replace_datetime_placeholder(suffix)

        is_custom_dir = output_settings.get("use_custom_output_dir", False)
        output_dir = (
            output_settings.get("output_directory", "")
            if is_custom_dir
            else output_settings.get("default_directory", "")
            or get_downloads_directory()
        )

        is_batch = self.main_window.analyze_tab.is_batch() and isinstance(
            self.main_window.current_result_data, list
        )

        if is_batch:
            try:
                selected_folder_path = (
                    self.main_window.analyze_tab.get_selected_folder()
                )
                if selected_folder_path:
                    folder_name = os.path.basename(selected_folder_path)
                    output_dir = os.path.join(
                        output_dir, f"{prefix}{folder_name}{suffix}"
                    )
                os.makedirs(output_dir, exist_ok=True)
                success_count = 0
                for (
                    filename,
                    success,
                    result_path_or_error,
                ) in self.main_window.current_result_data:
                    if (
                        success
                        and result_path_or_error
                        and os.path.exists(result_path_or_error)
                    ):
                        ext = os.path.splitext(result_path_or_error)[1] or ".txt"
                        base_name = os.path.splitext(filename)[0]
                        output_filename = f"{prefix}{base_name}{suffix}{ext}"
                        output_path = os.path.join(output_dir, output_filename)

                        with open(
                            result_path_or_error, "r", encoding="utf-8"
                        ) as src_file:
                            content = src_file.read()
                            content = content.replace("\r\n", "\n")
                            with open(output_path, "wb") as dst_file:
                                dst_file.write(content.encode("utf-8"))
                        success_count += 1

                if is_custom_dir:
                    msg_box = QMessageBox(self.main_window)
                    msg_box.setWindowTitle("ダウンロード完了")
                    msg_box.setText(
                        f"{success_count}個のファイルを設定出力先にダウンロードしました"
                    )
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    self._style_message_box_buttons(msg_box)
                    msg_box.exec_()
                else:
                    msg_box = QMessageBox(self.main_window)
                    msg_box.setWindowTitle("ダウンロード完了")
                    msg_box.setText(
                        f"{success_count}個のファイルのダウンロードが完了しました"
                    )
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    self._style_message_box_buttons(msg_box)
                    msg_box.exec_()
            except Exception as e:
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("保存エラー")
                msg_box.setText(f"ファイルの保存に失敗しました: {str(e)}")
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec_()
        else:
            try:
                input_path = self.main_window.analyze_tab.get_input_path_display()
                base_name = (
                    os.path.splitext(os.path.basename(input_path))[0]
                    if input_path and os.path.isfile(input_path)
                    else "analyzed"
                )
                output_filename = f"{prefix}{base_name}{suffix}.txt"
                output_path = os.path.join(output_dir, output_filename)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                complete_content = getattr(
                    self.main_window,
                    "complete_result_text",
                    self.main_window.current_result_text,
                )
                content = complete_content.replace("\r\n", "\n")

                if "===プレビューはここまでです===" in content:
                    content = content.split("\n===プレビューはここまでです===")[0]

                with open(output_path, "wb") as f:
                    f.write(content.encode("utf-8"))

                if is_custom_dir:
                    msg_box = QMessageBox(self.main_window)
                    msg_box.setWindowTitle("ダウンロード完了")
                    msg_box.setText("設定出力先へダウンロードしました")
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    self._style_message_box_buttons(msg_box)
                    msg_box.exec_()
                else:
                    msg_box = QMessageBox(self.main_window)
                    msg_box.setWindowTitle("ダウンロード完了")
                    msg_box.setText("ダウンロードが完了しました")
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    self._style_message_box_buttons(msg_box)
                    msg_box.exec_()
            except Exception as e:
                msg_box = QMessageBox(self.main_window)
                msg_box.setWindowTitle("保存エラー")
                msg_box.setText(f"ファイルの保存に失敗しました: {str(e)}")
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setStandardButtons(QMessageBox.Ok)
                self._style_message_box_buttons(msg_box)
                msg_box.exec_()

    def _style_message_box_buttons(self, msg_box):
        for button in msg_box.buttons():
            apply_button_style(button, "small")
