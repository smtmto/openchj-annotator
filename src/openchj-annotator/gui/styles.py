import os

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

DEFAULT_FONT_FAMILY = "Yu Gothic UI"


def get_minimal_style():
    return f"""
QWidget {{
    background-color: #F0F0F0;
    color: #333333;
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 14px;
}}
QMessageBox QPushButton {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 14px;
    background-color: #f0f0f0;
    border: 1px solid #adadad;
    border-radius: 2px;
    padding: 5px 16px;
    min-width: 75px;
}}
QMessageBox QPushButton:hover {{
    background-color: #e5f1fb;
    border-color: #adadad;
}}
QMessageBox QPushButton:focus {{
    border: 1px solid #adadad;
    outline: none;
}}
QMessageBox QPushButton:pressed {{
    background-color: #cce4f7;
    border-color: #adadad;
}}
QMainWindow {{
    background-color: #F0F0F0;
}}
QTabWidget::pane {{
    border: 1px solid #C0C0C0;
    background: #F0F0F0;
}}
QTabBar::tab {{
    background: #D0D0D0;
    border: 1px solid #B0B0B0;
    padding: 8px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: #F0F0F0;
    border-bottom: 1px solid #F0F0F0;
    font-weight: bold;
    margin-bottom: -1px;
}}
QTabBar::tab:hover {{
    background: #D8D8D8;
}}
QGroupBox {{
    border: 1px solid #C0C0C0;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
    background-color: #F0F0F0;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}
QDialog {{
    background-color: #F0F0F0;
}}
"""


def get_tab_style_definitions():
    return {
        "min_width": 80,
        "stylesheet": """
QTabWidget::pane {
    border: 1px solid #b0b0b0;
    background-color: #F0F0F0;
    position: relative;
    top: -1px;
}
QTabBar {
    background-color: transparent;
}
QTabBar::tab {
    min-width: 80px;
    padding: 6px 16px;
    margin-right: 1px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border-left: 1px solid #a0a0a0;
    border-right: 1px solid #a0a0a0;
    border-top: 1px solid #a0a0a0;
    border-bottom: none;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #e0e0e0, stop:1 #d0d0d0);
    color: #555555;
}
QTabBar::tab:first {
    margin-left: 5px;
}
QTabBar::tab:!selected:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffffff, stop:1 #f0f0f0);
    color: #222222;
    border-left-color: #b0b0b0;
    border-right-color: #b0b0b0;
    border-top-color: #b0b0b0;
}
QTabBar::tab:selected {
    background-color: #F0F0F0;
    color: #222222;
    font-weight: bold;
    border-left: 1px solid #b0b0b0;
    border-right: 1px solid #b0b0b0;
    border-top: 1px solid #b0b0b0;
    border-bottom: 1px solid #F0F0F0;
    padding: 6px 16px 7px 16px;
    margin-bottom: -1px;
}
QTabBar::tab:selected:hover {
}
QTabBar::scroller { width: 18px; }
QTabBar QToolButton { background-color: #f0f0f0; border: 1px solid #c0c0c0; border-radius: 2px; padding: 2px; }
QTabBar QToolButton:hover { background-color: #e0e0e0; }
    """,
    }


def get_button_style_definitions():
    return {
        "default": {
            "stylesheet": f"""
QPushButton {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 12px;
    background-color: white;
    color: #333333;
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 4px 10px;
    margin: 0;
    min-height: 24px;
}}
QPushButton:hover {{
    background-color: #F5F5F5;
    border-color: #AAAAAA;
}}
QPushButton:pressed {{
    background-color: #E5E5E5;
    border-color: #999999;
}}
QPushButton:disabled {{
    background-color: #F0F0F0;
    color: #AAAAAA;
    border-color: #DDDDDD;
}}
"""
        },
        "primary": {
            "stylesheet": f"""
QPushButton {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 14px;
    background-color: white;
    color: #333333;
    border: 1px solid #0078D7;
    border-radius: 5px;
    padding: 4px 10px;
    margin: 0;
    min-height: 24px;
}}
QPushButton:hover {{
    background-color: #E8F1F8;
    border-color: #106EBE;
}}
QPushButton:pressed {{
    background-color: #D0E1F0;
    border-color: #005A9E;
}}
QPushButton:disabled {{
    background-color: #F0F0F0;
    color: #AAAAAA;
    border-color: #DDDDDD;
}}
"""
        },
        "secondary": {
            "stylesheet": f"""
QPushButton {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 12px;
    background-color: white;
    color: #333333;
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 2px 6px;
    margin: 0;
}}
QPushButton:hover {{
    background-color: #F5F5F5;
    border-color: #AAAAAA;
}}
QPushButton:pressed {{
    background-color: #E5E5E5;
    border-color: #999999;
}}
QPushButton:disabled {{
    background-color: #F0F0F0;
    color: #AAAAAA;
    border-color: #DDDDDD;
}}
"""
        },
        "config": {
            "stylesheet": f"""
QPushButton {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 12px;
    background-color: white;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 5px;
    padding: 2px 6px;
}}
QPushButton:hover {{
    background-color: #F5F5F5;
    border-color: #AAAAAA;
}}
QPushButton:pressed {{
    background-color: #E5E5E5;
    border-color: #999999;
}}
QPushButton:disabled {{
    background-color: #F0F0F0;
    color: #AAAAAA;
    border-color: #DDDDDD;
}}
"""
        },
        "small": {
            "stylesheet": f"""
QPushButton {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 12px;
    background-color: white;
    color: #333333;
    border: 1px solid #CCCCCC;
    border-radius: 3px;
    padding: 2px 6px;
    margin-right: 8px;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: #F5F5F5;
    border-color: #AAAAAA;
}}
QPushButton:pressed {{
    background-color: #E5E5E5;
    border-color: #999999;
}}
QPushButton:disabled {{
    background-color: #F0F0F0;
    color: #AAAAAA;
    border-color: #DDDDDD;
}}
"""
        },
        "disabled": {
            "stylesheet": f"""
QPushButton {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 12px;
    background-color: #F0F0F0;
    color: #AAAAAA;
    border: 1px solid #DDDDDD;
    border-radius: 5px;
    padding: 2px 6px;
    margin: 0;
    min-height: 24px;
}}
"""
        },
    }


def get_input_style_definitions():
    return {
        "min_height": 24,
        "stylesheet": """
    QLineEdit {
        background-color: white;
        border: 1px solid #C0C0C0;
        border-radius: 4px;
        padding: 4px;
        min-height: 24px;
    }
    QLineEdit:focus {
        border: 1px solid #808080;
    }
    QLineEdit:disabled {
        background-color: #f0f0f0;
        border: 1px solid #d0d0d0;
        color: #888888;
    }
    """,
    }


def get_label_style_definitions():
    return {
        "default": {
            "stylesheet": f"""
QLabel {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 11px;
    line-height: 1.2;
    min-height: 24px;
    color: #333333;
    text-align: left;
    margin-bottom: 2px;
}}
"""
        },
        "header": {
            "stylesheet": f"""
QLabel {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 14px;
    line-height: 1.2;
    min-height: 32px;
    font-weight: bold;
    color: #333333;
    text-align: left;
    margin-bottom: 4px;
}}
"""
        },
        "header_bold": {
            "stylesheet": f"""
QLabel {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    border: none;
    font-weight: bold;
    margin-bottom: 0px;
}}
"""
        },
        "stats": {
            "stylesheet": f"""
QLabel {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 12px;
    line-height: 1.2;
    padding-top: 2px;
    margin-left: 12px;
    min-height: 24px;
    color: #666666;
}}
"""
        },
        "info": {
            "stylesheet": f"""
QLabel {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 10px;
    line-height: 1.2;
    min-height: 20px;
    color: #555555;
}}
"""
        },
        "filename": {
            "stylesheet": f"""
QLabel {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: 13px;
    line-height: 1.2;
    min-height: 20px;
    color: #333333;
}}
"""
        },
    }


SCROLL_AREA_STYLE = {
    "stylesheet": """
    QScrollArea { background-color: #F0F0F0; }
    QScrollBar:vertical {
        border: none;
        background: #F0F0F0;
        width: 12px;
        margin: 15px 0 15px 0;
    }
    QScrollBar::handle:vertical {
        background: #C0C0C0;
        min-height: 20px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical:hover {
        background: #A0A0A0;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    QScrollBar:horizontal {
        border: none;
        background: #F0F0F0;
        height: 12px;
        margin: 0 15px 0 15px;
    }
    QScrollBar::handle:horizontal {
        background: #C0C0C0;
        min-width: 20px;
        border-radius: 3px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #A0A0A0;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    """
}

SCROLL_CONTENT_STYLE = {
    "stylesheet": """
    QWidget {
        background-color: #F0F0F0;
    }
    """
}

FRAME_STYLE = {
    "default": {
        "stylesheet": """
        QFrame {
            background-color: #f0f0f0;
            border: none;
            border-radius: 0px;
        }
        """
    },
    "separator": {
        "stylesheet": """
        QFrame {
            background-color: #D0D0D0;
            margin-top: 5px;
            margin-bottom: 10px;
        }
        """
    },
}

TEXT_AREA_STYLE = {
    "padding": 8,
    "stylesheet": """
QScrollBar:vertical {
    border: none;
    background: #F0F0F0;
    width: 12px;
    margin: 15px 0 15px 0;
}
QScrollBar::handle:vertical {
    background: #C0C0C0;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #A0A0A0;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QScrollBar:horizontal {
    border: none;
    background: #F0F0F0;
    height: 12px;
    margin: 0 15px 0 15px;
}
QScrollBar::handle:horizontal {
    background: #C0C0C0;
    min-width: 20px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #A0A0A0;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
""",
}


def get_table_style_definitions():
    target_header_font_size_pt = 9
    target_cell_font_size_pt = 9
    return f"""
QTableWidget {{
    border: 1px solid #C0C0C0;
}}
QScrollBar:vertical {{
    border: none;
    background: #F0F0F0;
    width: 12px;
    margin: 15px 0 15px 0;
}}
QScrollBar::handle:vertical {{
    background: #C0C0C0;
    min-height: 20px;
    border-radius: 3px;
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}
QScrollBar:horizontal {{
    border: none;
    background: #F0F0F0;
    height: 12px;
    margin: 0 15px 0 15px;
}}
QScrollBar::handle:horizontal {{
    background: #C0C0C0;
    min-width: 20px;
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
}}
QHeaderView::section {{
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: {target_header_font_size_pt}pt;
}}
QTableWidget::item {{  
    font-family: "{DEFAULT_FONT_FAMILY}";
    font-size: {target_cell_font_size_pt}pt;
}}
"""


def get_combobox_style_definitions():
    return {
        "stylesheet": """
    QComboBox {
        background-color: white;
        border: 1px solid #C0C0C0;
        border-radius: 4px;
        padding: 4px;
        min-height: 24px;
    }
    QComboBox:hover {
        background-color: #fafafa;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #C0C0C0;
    }
    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        border: none;
        selection-background-color: #e6e6e6;
        outline: none;
    }
    QComboBox QAbstractItemView::item {
        border: none;
        padding: 4px 8px;
    }
    QComboBox QAbstractItemView::item:hover {
        background-color: #f0f0f0;
        border: none;
    }
    QComboBox QAbstractItemView::item:selected {
        background-color: #e6e6e6;
        border: none;
    }
    """
    }


def get_dialog_style_definitions():
    return {
        "stylesheet": f"""
    QDialog {{
        background-color: #F0F0F0;
        color: #333333;
        font-size: 12px;
        font-family: "{DEFAULT_FONT_FAMILY}", 'Yu Gothic UI', sans-serif;
    }}
    QDialog QLabel, QDialog QPushButton, QDialog QCheckBox, QDialog QLineEdit, QDialog QFrame {{
        background-color: transparent;
        color: #333333;
        font-size: 12px;
        font-family: "{DEFAULT_FONT_FAMILY}", 'Yu Gothic UI', sans-serif;
        border: none;
    }}
    QDialog QFrame {{
        border: 1px solid #C0C0C0;
        background-color: #F0F0F0;
        border-radius: 2px;
    }}
    QDialog QPushButton {{
        font-family: "{DEFAULT_FONT_FAMILY}", 'Yu Gothic UI', sans-serif;
        font-size: 12px;
        background-color: white;
        border: 1px solid #CCCCCC;
        border-radius: 3px;
        padding: 4px 8px;
        color: #333333;
    }}
    QDialog QPushButton:hover {{
        background-color: #f5f5f5;
    }}
    """
    }


PROGRESS_STYLE = {
    "height": 20,
    "color": "#4CAF50",
}


def get_checkbox_style_definitions():
    return {
        "stylesheet": """
    QCheckBox {
        background-color: transparent;
    }
    """,
        "smaller_font": {
            "stylesheet": """
    QCheckBox {
        background-color: transparent;
        font-size: 12px;
    }
    """
        },
    }


HELP_BUTTON_STYLESHEET = """
QPushButton {
    background-color: #f0f0f0;
    border: 1px solid #c0c0c0;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
    padding: 0px;
}
QPushButton:hover {
    background-color: #e0e0e0;
}
"""
HELP_BUTTON_FIXED_SIZE = (18, 18)


def get_tag_special_settings_style_definitions():
    return {
        "input_frame": {"stylesheet": "QFrame { border: none; }"},
        "label": {
            "stylesheet": f'QLabel {{ font-family: "{DEFAULT_FONT_FAMILY}"; border: none; }}'
        },
        "special_settings_combo": {
            "stylesheet": f"""
    QComboBox {{
        font-family: "{DEFAULT_FONT_FAMILY}";
        font-size: 12px;
        min-height: 24px;
        background-color: white;
        color: #000000;
    }}
    QComboBox:hover {{ background-color: #e0e0e0; }}
    QComboBox QAbstractItemView {{
        font-family: "{DEFAULT_FONT_FAMILY}";
        background-color: #f5f5f5;
        border: 1px solid #c0c0c0;
    }}
    QComboBox QAbstractItemView::item {{
        font-family: "{DEFAULT_FONT_FAMILY}";
        background-color: #ffffff;
        color: #000000;
        padding: 4px 8px;
    }}
    QComboBox QAbstractItemView::item:hover {{ background-color: #f5f5f5; }}
    QComboBox QAbstractItemView::item:selected {{ background-color: #d0eaff; color: #000000; }}
    """
        },
        "tag_content_edit": {
            "stylesheet": f'QLineEdit {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; padding: 2px 2px; border: 1px solid #ccc; border-radius: 3px; min-height: 24px; background-color: #ffffff; }}'
        },
        "surface_form_edit": {
            "stylesheet": f'QLineEdit {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; padding: 2px 2px; border: 1px solid #ccc; border-radius: 3px; min-height: 24px; background-color: #ffffff; }}'
        },
        "add_button": {
            "stylesheet": f'QPushButton {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; padding: 2px 6px; border: 1px solid #c0c0c0; border-radius: 3px; min-height: 24px; }}'
        },
        "pattern_text": {
            "stylesheet": f'QLineEdit {{ font-family: "{DEFAULT_FONT_FAMILY}"; background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 3px; padding: 3px 5px; }}'
        },
        "delete_button": {
            "stylesheet": f'QPushButton {{ font-family: "{DEFAULT_FONT_FAMILY}"; min-height: 0px; padding: 0px; border: 1px solid #ccc; border-radius: 3px; }}'
        },
    }


def get_text_areas_style_definitions():
    return {
        "main_splitter": {
            "stylesheet": "QSplitter {border: none;} QSplitter::handle:vertical { background-color: #F0F0F0; border-bottom: 1px solid lightgray; height: 1px; margin: 10px 5px 10px 5px; }"
        },
        "top_splitter": {
            "stylesheet": "QSplitter { border: none; } QSplitter::handle:horizontal { background-color: #F0F0F0; border: none; width: 1px; margin: 50px 5px 10px 5px; }"
        },
        "text_edit": {
            "stylesheet": """QTextEdit { background-color: white; border: 1px solid #C0C0C0; border-radius: 4px; } QScrollBar:vertical { border: none; background: #F0F0F0; width: 12px; margin: 15px 0 15px 0; } QScrollBar::handle:vertical { background: #C0C0C0; min-height: 20px; border-radius: 3px; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; } QScrollBar:horizontal { border: none; background: #F0F0F0; height: 12px; margin: 0 15px 0 15px; } QScrollBar::handle:horizontal { background: #C0C0C0; min-width: 20px; border-radius: 3px; } QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }"""
        },
        "stats_label": {
            "stylesheet": f"""QLabel {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; color: #666666; padding-bottom: 2px;}}"""
        },
        "output_stats_label": {
            "stylesheet": f"""QLabel {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; color: #666666; padding-bottom: 2px; max-width: 700px;}}"""
        },
        "processing_status_label": {
            "stylesheet": f"""QLabel {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; color: #336633; font-weight: bold; background-color: #EEFFEE; border: 1px solid #CCDDCC; border-radius: 4px; padding: 5px; margin: 5px 0;}}"""
        },
    }


def get_message_box_style_definitions():
    return {
        "default": {
            "stylesheet": f"""QMessageBox {{ border: none; }} QMessageBox QLabel {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 14px; border: none; }}"""
        }
    }


def get_regex_settings_style_definitions():
    return {
        "pattern_label": {
            "stylesheet": f'QLabel {{ font-family: "{DEFAULT_FONT_FAMILY}"; border: none; }}'
        },
        "pattern_entry": {
            "stylesheet": f'QLineEdit {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; padding: 2px 2px; border: 1px solid #ccc; border-radius: 3px; min-height: 24px; }}'
        },
        "add_button": {
            "stylesheet": f'QPushButton {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; padding: 2px 6px; border: 1px solid #c0c0c0; border-radius: 3px; min-height: 24px; }}'
        },
        "pattern_display": {
            "stylesheet": f'QLineEdit {{ font-family: "{DEFAULT_FONT_FAMILY}"; background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 3px; padding: 3px 5px; }}'
        },
        "delete_button": {
            "stylesheet": f'QPushButton {{ font-family: "{DEFAULT_FONT_FAMILY}"; min-height: 0px; padding: 0px; border: 1px solid #ccc; border-radius: 3px; font-size: 10px; }} QPushButton:hover {{ background-color: #e8e8e8; }}'
        },
        "enabled_entry": {
            "stylesheet": f'QLineEdit {{ font-family: "{DEFAULT_FONT_FAMILY}"; background-color: white; color: #333333; border: 1px solid #ccc; border-radius: 3px; min-height: 24px; font-size: 12px; padding: 2px 2px; }}'
        },
        "disabled_entry": {
            "stylesheet": f'QLineEdit {{ font-family: "{DEFAULT_FONT_FAMILY}"; background-color: #f0f0f0; color: #888888; border: 1px solid #d0d0d0; border-radius: 3px; min-height: 24px; font-size: 12px; padding: 2px 2px; }}'
        },
        "enabled_add_button": {
            "stylesheet": f'QPushButton {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; padding: 2px 6px; border: 1px solid #c0c0c0; border-radius: 3px; min-height: 24px; background-color: white; color: #333333; }} QPushButton:hover {{ background-color: #f5f5f5; }}'
        },
        "disabled_add_button": {
            "stylesheet": f'QPushButton {{ font-family: "{DEFAULT_FONT_FAMILY}"; font-size: 12px; padding: 2px 6px; border: 1px solid #d0d0d0; border-radius: 3px; min-height: 24px; background-color: #f0f0f0; color: #AAAAAA; }}'
        },
    }


def setup_font():
    global DEFAULT_FONT_FAMILY
    font_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "resources",
        "fonts",
        "NotoSansJP-Regular.ttf",
    )
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                font_family_from_file = font_families[0]
                app = QApplication.instance()
                if app:
                    default_font_obj = QFont(font_family_from_file)
                    default_font_obj.setStyleStrategy(QFont.PreferAntialias)
                    default_font_obj.setHintingPreference(QFont.PreferNoHinting)
                    app.setFont(default_font_obj)
                DEFAULT_FONT_FAMILY = font_family_from_file
                return DEFAULT_FONT_FAMILY
    return DEFAULT_FONT_FAMILY


def apply_button_style(button, style_type="default"):
    button_styles = get_button_style_definitions()
    sheet = button_styles.get(style_type, button_styles["default"])["stylesheet"]
    button.setStyleSheet(sheet)


def apply_label_style(label, style_type="default"):
    label_styles = get_label_style_definitions()
    sheet_definition = label_styles.get(style_type, label_styles["default"])
    sheet = sheet_definition["stylesheet"]
    label.setStyleSheet(sheet)


def apply_text_area_style(text_area):
    text_area.setFont(QFont(DEFAULT_FONT_FAMILY, 14))
    base_style = f"padding: {TEXT_AREA_STYLE['padding']}px;"
    if "stylesheet" in TEXT_AREA_STYLE:
        base_style += TEXT_AREA_STYLE["stylesheet"]
    text_area.setStyleSheet(base_style)


def apply_table_scrollbar_style(table):
    table.setStyleSheet(get_table_style_definitions())


def apply_input_style(input_field):
    input_field.setFont(QFont(DEFAULT_FONT_FAMILY, 14))
    input_style_defs = get_input_style_definitions()
    if "min_height" in input_style_defs:
        input_field.setMinimumHeight(input_style_defs["min_height"])
    if "stylesheet" in input_style_defs:
        input_field.setStyleSheet(input_style_defs["stylesheet"])


def apply_checkbox_style(checkbox, style_type="default"):
    checkbox.setFont(QFont(DEFAULT_FONT_FAMILY, 14))
    checkbox_style_defs = get_checkbox_style_definitions()
    if style_type == "smaller_font" and checkbox_style_defs.get("smaller_font", {}).get(
        "stylesheet"
    ):
        checkbox.setStyleSheet(checkbox_style_defs["smaller_font"]["stylesheet"])
    elif checkbox_style_defs.get("stylesheet"):
        checkbox.setStyleSheet(checkbox_style_defs["stylesheet"])


def apply_combobox_style(combobox):
    combobox.setFont(QFont(DEFAULT_FONT_FAMILY, 14))
    combobox_style_defs = get_combobox_style_definitions()
    if combobox_style_defs.get("stylesheet"):
        combobox.setStyleSheet(combobox_style_defs["stylesheet"])


def apply_tab_style(tab_widget):
    tab_bar = tab_widget.tabBar()
    tab_bar.setFont(QFont(DEFAULT_FONT_FAMILY, 14))
    tab_style_def = get_tab_style_definitions()
    if tab_style_def.get("min_width"):
        tab_bar.setMinimumWidth(tab_style_def["min_width"])
    tab_bar.setStyleSheet(tab_style_def["stylesheet"])


def apply_dialog_style(dialog):
    dialog_style_defs = get_dialog_style_definitions()
    dialog.setStyleSheet(dialog_style_defs["stylesheet"])


def apply_scroll_area_style(scroll_area):
    if SCROLL_AREA_STYLE.get("stylesheet"):
        scroll_area.setStyleSheet(SCROLL_AREA_STYLE["stylesheet"])


def apply_scroll_content_style(widget):
    if SCROLL_CONTENT_STYLE.get("stylesheet"):
        widget.setStyleSheet(SCROLL_CONTENT_STYLE["stylesheet"])


def apply_frame_style(frame, style_type="default"):
    if FRAME_STYLE.get(style_type, {}).get("stylesheet"):
        frame.setStyleSheet(FRAME_STYLE[style_type]["stylesheet"])


def apply_progress_style(progress_bar, is_folder=False):
    if PROGRESS_STYLE.get("height"):
        progress_bar.setMinimumHeight(PROGRESS_STYLE["height"])
    if PROGRESS_STYLE.get("color"):
        progress_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {PROGRESS_STYLE['color']}; }}"
        )


def get_combo_style():
    combobox_style_defs = get_combobox_style_definitions()
    base_stylesheet = combobox_style_defs["stylesheet"]
    icon_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
            "images",
            "combo_triangle.png",
        )
    )
    if os.path.exists(icon_path):
        return (
            base_stylesheet
            + f"QComboBox::down-arrow {{ image: url({icon_path.replace(os.sep, '/')}); }}"
        )
    return base_stylesheet


def apply_message_box_style(msg_box, style_type="default"):
    message_box_styles = get_message_box_style_definitions()
    if style_type in message_box_styles:
        msg_box.setStyleSheet(message_box_styles[style_type]["stylesheet"])
    for button in msg_box.buttons():
        apply_button_style(button, "small")


def apply_tag_special_settings_style(widget, style_type):
    tag_styles = get_tag_special_settings_style_definitions()
    if style_type in tag_styles:
        widget.setStyleSheet(tag_styles[style_type]["stylesheet"])


def apply_text_areas_style(widget, style_type):
    text_areas_styles = get_text_areas_style_definitions()
    if style_type in text_areas_styles:
        widget.setStyleSheet(text_areas_styles[style_type]["stylesheet"])


def apply_regex_settings_style(widget, style_type):
    regex_styles = get_regex_settings_style_definitions()
    if style_type in regex_styles:
        widget.setStyleSheet(regex_styles[style_type]["stylesheet"])
