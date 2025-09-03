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


class AnalysisWorker(QThread):
    message = Signal(str)
    finished = Signal(str, list)
    error = Signal(str)
    start_animation = Signal(str)

    stop_animation = Signal()

    def __init__(self, analyzer, text, text_source=None):
        super().__init__()
        self.analyzer = analyzer
        self.text = text
        self.text_source = text_source

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
        try:
            if not self.text or not self.text.strip():
                self.error.emit("解析するテキストがありません。")
                return

            self.start_animation.emit("テキストを解析しています")
            results = self.analyzer.analyze(self.text)
            self.stop_animation.emit()

            if not results:
                self.error.emit(
                    "解析結果が空です。形態素解析に失敗した可能性があります。"
                )
                return

            self.start_animation.emit("結果をフォーマットしています")
            from utils.file_utils import extract_filename_from_path

            filename = (
                extract_filename_from_path(self.text_source)
                if self.text_source
                else "manual_input.txt"
            )
            result_text = self.analyzer.format_as_tsv(results, filename)
            self.stop_animation.emit()
            self.finished.emit(result_text, results)

        except Exception as e:
            self.stop_animation.emit()
            self.error.emit(str(e))
