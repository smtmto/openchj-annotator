import logging
import os

from analyzer import OpenCHJAnnotator
from gui.styles import DEFAULT_FONT_FAMILY, apply_tab_style
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QFrame,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from utils.path_manager import get_resource_path

from .components.analyze_output_tab_widget import AnalyzeOutputTabWidget
from .components.settings_tab_widget import SettingsTabWidget
from .controllers.analysis_controller import AnalysisController
from .controllers.ui_controller import UIController


class MainWindow(QMainWindow):
    def __init__(self, config=None):
        super().__init__()
        self.setWindowTitle("OpenCHJAnnotator 0.6.0")
        self.setMinimumSize(600, 500)
        self.resize(940, 760)
        self.font_family = DEFAULT_FONT_FAMILY
        self.config = config
        self.check_dictionary_paths()

        self.analyzer = None
        self.analyze_tab = None
        self.settings_tab = None
        self.setup_ui()
        self.initialize_analyzer()

        self.analysis_controller = AnalysisController(self)
        self.ui_controller = UIController(self)

        self.hidden_webview = QWebEngineView(self)
        self.hidden_webview.setFixedSize(1, 1)
        self.hidden_webview.setVisible(False)
        self.hidden_webview.setHtml("<html><body>Preloading...</body></html>")
        self.check_first_run()

        self.current_result_text = None
        self.complete_result_text = None
        self.current_result_data = None

    def check_dictionary_paths(self):
        if self.config is None:
            return

        custom_dict_path = self.config.get_unidic_path("dic")
        if custom_dict_path and not os.path.exists(custom_dict_path):
            if self.config.get_active_dictionary() == "dic":
                self.config.set_active_dictionary("lite")

    def setup_font(self):
        self.font_family = DEFAULT_FONT_FAMILY

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 2, 15, 15)
        main_layout.setSpacing(2)
        self.tab_widget = QTabWidget()
        apply_tab_style(self.tab_widget)
        main_layout.addWidget(self.tab_widget, 1)

        self.analyze_tab = AnalyzeOutputTabWidget()
        self.tab_widget.addTab(self.analyze_tab, "解析")
        self._connect_analyze_tab_signals()

        self.settings_tab = SettingsTabWidget(self.config)
        self.tab_widget.addTab(self.settings_tab, "設定")
        self._connect_settings_tab_signals()

        icon_path = get_resource_path("images", "icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.tab_seamline = QFrame()
        self.tab_seamline.setFrameShape(QFrame.HLine)
        self.tab_seamline.setFixedHeight(1)
        self.tab_seamline.setStyleSheet("background-color: #F0F0F0; border: none;")
        self.tab_seamline.setParent(self)
        self.tab_widget.currentChanged.connect(self.adjust_tab_seamline)
        QTimer.singleShot(
            0, lambda: self.adjust_tab_seamline(self.tab_widget.currentIndex())
        )

    def _connect_analyze_tab_signals(self):
        import logging

        if not self.analyze_tab:
            logging.warning("analyze_tabが存在しないのでシグナル接続をスキップします")
            return

        self.analyze_tab.file_selected.connect(self.handle_file_selected)
        self.analyze_tab.folder_selected.connect(self.handle_folder_selected)
        self.analyze_tab.preview_requested.connect(self.handle_preview_requested)
        self.analyze_tab.selection_cleared.connect(self.handle_selection_cleared)
        self.analyze_tab.input_text_changed.connect(self.handle_input_text_changed)
        self.analyze_tab.format_settings_clicked.connect(self.show_format_settings)
        self.analyze_tab.analyze_clicked.connect(self.start_analysis)
        self.analyze_tab.download_clicked.connect(self.download_result)
        self.analyze_tab.clear_clicked.connect(self.clear_all_content)
        self.analyze_tab.output_format_changed.connect(
            self.handle_output_format_changed
        )

    def _connect_settings_tab_signals(self):
        if not self.settings_tab:
            return
        self.settings_tab.dictionary_changed.connect(lambda: self.initialize_analyzer())
        self.settings_tab.show_user_dict_help_requested.connect(
            self.show_user_dict_help
        )
        self.settings_tab.open_download_page_requested.connect(
            self.show_custom_dict_help
        )

    def adjust_tab_seamline(self, index):
        tab_bar = self.tab_widget.tabBar()
        if not tab_bar or index < 0 or index >= tab_bar.count():
            return
        tab_rect = tab_bar.tabRect(index)
        tab_pos = tab_bar.pos()
        if index == 0:
            x = tab_pos.x() + tab_rect.x() + 21
        else:
            x = tab_pos.x() + tab_rect.x() + 16
        y = tab_pos.y() + tab_rect.height() + 2
        if index == 0:
            width = tab_rect.width() - 8
        else:
            width = tab_rect.width() - 3
        self.tab_seamline.setGeometry(x, y, width, 2)
        self.tab_seamline.raise_()
        self.tab_seamline.show()
        if index == 1 and self.settings_tab:
            self.settings_tab.update_controls_state()

    def handle_file_selected(self, filenames):
        self.analysis_controller.handle_file_selected(filenames)
        self.analyze_tab.text_areas_widget.set_input_text_readonly(True)

    def handle_folder_selected(self, folder_path):
        self.analysis_controller.handle_folder_selected(folder_path)
        self.analyze_tab.text_areas_widget.set_input_text_readonly(True)

    def handle_preview_requested(self, file_path):
        try:
            self.analysis_controller.load_preview(file_path)
        finally:
            if self.analyze_tab:
                self.analyze_tab.hide_loading_message()

    def handle_selection_cleared(self):
        self.ui_controller.handle_selection_cleared()
        self.analyze_tab.text_areas_widget.set_input_text_readonly(False)

    def handle_input_text_changed(self):
        self.ui_controller.handle_input_text_changed()

    def show_format_settings(self):
        self.ui_controller.show_format_settings()

    def start_analysis(self):
        self.analysis_controller.start_analysis()

    def download_result(self):
        output_format = self.analyze_tab.get_output_format()
        self.analysis_controller.download_result(output_format)

    def handle_output_format_changed(self, format_type):
        self.analysis_controller.handle_output_format_changed(format_type)

    def clear_all_content(self):
        self.analyze_tab.setEnabled(False)
        self.analyze_tab.clear_all_content_display()
        self.current_result_text = None
        self.complete_result_text = None
        self.current_result_data = None

        if self.analyzer and hasattr(self.analyzer, "tag_processor"):
            self.analyzer.tag_processor.tag_info = []

        if (
            hasattr(self.ui_controller, "preview_timer")
            and self.ui_controller.preview_timer
        ):
            self.ui_controller.preview_timer.stop()
            self.ui_controller.preview_timer.deleteLater()
            self.ui_controller.preview_timer = None

        self.analyze_tab.text_areas_widget.set_input_text_readonly(False)

        import gc

        gc.collect()

        QTimer.singleShot(100, lambda: self.analyze_tab.setEnabled(True))

    def show_user_dict_help(self):
        self.ui_controller.show_user_dict_help()

    def show_custom_dict_help(self):
        self.ui_controller.show_custom_dict_help()

    def initialize_analyzer(self):
        try:
            if self.config is None:
                logging.warning(
                    "initialize_analyzer: config is not set, skipping initialization"
                )
                return

            self.analyzer = OpenCHJAnnotator(self.config)

            if self.analyze_tab and hasattr(self, "ui_controller"):
                try:
                    self.ui_controller._update_preview_now()
                except Exception as preview_e:
                    logging.warning(f"Error during initial preview update: {preview_e}")

            if hasattr(self, "ui_controller"):
                self.ui_controller.update_analyze_button_state()

        except Exception as e:
            error_msg = f"アナライザーの初期化に失敗しました: {str(e)}"
            QMessageBox.critical(self, "初期化エラー", error_msg)
            self.analyzer = None

            if hasattr(self, "ui_controller"):
                try:
                    self.ui_controller.update_analyze_button_state()
                except Exception as ui_e:
                    logging.error(
                        f"Error updating UI after analyzer init failed: {ui_e}"
                    )

    def check_first_run(self):
        pass

    def close_event(self, event):
        event.accept()
