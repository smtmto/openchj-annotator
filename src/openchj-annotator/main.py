import os
import sys

from gui import styles
from gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
from utils import path_manager

from config import Config


def main():
    app = QApplication(sys.argv)

    if os.name == "nt":
        app.setStyle("Fusion")

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
