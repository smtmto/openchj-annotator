import os
import sys

from gui import styles
from gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication, QStyleFactory
from utils import path_manager

from config import Config


def main():
    app = QApplication(sys.argv)

    if os.name == "nt":
        available_styles = {style.lower(): style for style in QStyleFactory.keys()}
        if "windowsvista" in available_styles:
            app.setStyle(available_styles["windowsvista"])
        elif "windows" in available_styles:
            app.setStyle(available_styles["windows"])

    styles.setup_font()
    app.setStyleSheet(styles.get_minimal_style())

    if os.environ.get("OPENCHJ_IS_FROZEN", "0") == "1":
        config = Config()
    else:
        config_path = path_manager.get_effective_config_file_path("config.json")
        config = Config(str(config_path))

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
