import logging
import os
import time

from PySide6.QtCore import QObject, QThread, QTimer, Signal


class ProgressAnimation(QObject):
    update_message = Signal(str)

    def __init__(self, base_message):
        super().__init__()
        self.base_message = base_message
        self.dots = ["", ".", "..", "..."]
        self.current_index = 0
        self.timer = None

        self.is_running = False

    def start(self):
        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self._update_dots)

        self.is_running = True
        self.timer.start(400)
        self._update_dots()

    def stop(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        self.is_running = False

    def _update_dots(self):
        if not self.is_running:
            return

        message = f"{self.base_message}{self.dots[self.current_index]}"
        self.update_message.emit(message)
        self.current_index = (self.current_index + 1) % len(self.dots)


class BatchAnalysisWorker(QThread):
    progress = Signal(int, str)
    message = Signal(str)
    finished = Signal(list)
    error = Signal(str)
    start_animation = Signal(str)

    stop_animation = Signal()

    def __init__(
        self, analyzer, files, config, is_folder_processing=False, folder_path=None
    ):
        super().__init__()
        self.analyzer = analyzer
        self.files = files
        self.config = config
        self.is_folder_processing = is_folder_processing
        self.folder_path = folder_path

        self.animation = ProgressAnimation("")

        self.animation.update_message.connect(self.message)

        self.start_animation.connect(self._start_animation)
        self.stop_animation.connect(self._stop_animation)

    def _start_animation(self, message_base):
        self.animation.base_message = message_base
        self.animation.start()

    def _stop_animation(self):
        self.animation.stop()

    def run(self):
        results = []

        try:
            for i, file_path in enumerate(self.files):
                filename = os.path.basename(file_path)
                self.progress.emit(i + 1, filename)

                self.start_animation.emit(
                    f"処理中: {filename} ({i+1}/{len(self.files)})"
                )

                try:
                    import tempfile

                    fd, temp_path = tempfile.mkstemp(suffix=".txt")
                    os.close(fd)
                    from utils.file_utils import read_text_file, write_text_file

                    try:

                        text = read_text_file(file_path)
                        if not text.strip():
                            logging.warning(
                                f"Empty file was read as a result: {filename}"
                            )
                            results.append(
                                (
                                    filename,
                                    False,
                                    "The file is empty or all reading failed.",
                                )
                            )
                            continue

                        results_data = self.analyzer.analyze(text)

                        content = self.analyzer.format_as_tsv(results_data, filename)

                        write_text_file(content, temp_path, encoding="utf-8")
                        results.append((filename, True, temp_path))
                    except UnicodeDecodeError as ude:
                        logging.error(
                            f"Encoding error during batch processing: {ude} - {filename}"
                        )
                        results.append((filename, False, f"Encoding error: {str(ude)}"))
                    finally:

                        self.stop_animation.emit()
                except Exception as e:
                    results.append((filename, False, str(e)))
                    self.stop_animation.emit()

            self.start_animation.emit("処理完了")
            time.sleep(0.5)

            self.stop_animation.emit()

            self.finished.emit(results)

        except Exception as e:
            self.stop_animation.emit()
            logging.error(f"Batch processing error: {e}")
            self.error.emit(str(e))
