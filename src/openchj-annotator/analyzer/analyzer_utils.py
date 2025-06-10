import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Optional

_pm_module = None
try:
    from utils import path_manager as pm_mod

    _pm_module = pm_mod
except ImportError as e:
    logging.error(
        f"Could not import path_manager in analyzer.utils: {e}. "
        "This will likely cause issues finding resources."
    )


def load_jis_mapping() -> Dict[str, str]:
    jis_mapping_filename = "jis_mapping.json"

    if _pm_module:
        try:
            mapping_file_path = _pm_module.get_resource_path(
                "data", jis_mapping_filename
            )
            if mapping_file_path.exists() and mapping_file_path.is_file():
                with open(mapping_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logging.error(
                    f"jis_mapping.json NOT FOUND via path_manager at: {mapping_file_path}"
                )
        except Exception as e:
            logging.error(f"Error loading jis_mapping.json via path_manager: {e}")
    else:
        logging.error(
            "path_manager module is not available in analyzer.utils. Cannot load jis_mapping.json reliably."
        )

    try:
        current_dir = Path(__file__).resolve().parent
        fallback_path = (
            current_dir.parent.parent / "resources" / "data" / jis_mapping_filename
        )
        logging.warning(
            f"Attempting fallback load of jis_mapping.json from: {fallback_path}"
        )
        if fallback_path.exists() and fallback_path.is_file():
            with open(fallback_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            logging.error(
                f"jis_mapping.json NOT FOUND via fallback path: {fallback_path}"
            )
    except Exception as e_fallback:
        logging.error(f"Error in fallback load of jis_mapping.json: {e_fallback}")

    logging.critical(
        "CRITICAL: Failed to load jis_mapping.json. Aozora formatting will be incorrect."
    )
    return {}


def jis_to_unicode(jis_code_str_from_note: str, jis_mapping: Dict[str, str]) -> str:
    if not jis_mapping:
        logging.error("jis_mapping is EMPTY in jis_to_unicode. Cannot convert.")
        return ""

    match = re.search(r"第\d+水準(\d+)-(\d+)-(\d+)", jis_code_str_from_note)
    if match:
        page_str = match.group(1)
        row_str = match.group(2)
        cell_str = match.group(3)
        page_val = int(page_str)
        row_val = int(row_str)
        cell_val = int(cell_str)
        jis_key = f"{page_val}-{str(row_val).zfill(2)}-{str(cell_val).zfill(2)}"

        if jis_key in jis_mapping:
            unicode_char = jis_mapping[jis_key]
            return unicode_char
        else:
            logging.warning(
                f"  Key '{jis_key}' NOT FOUND in jis_mapping. Input: '{jis_code_str_from_note}'. Sample keys from json: {list(jis_mapping.keys())[:20]}"
            )
            return ""
    else:
        logging.warning(
            f"  Could not parse page-row-cell from JIS code string: '{jis_code_str_from_note}' (regex did not match)"
        )
        return ""


def get_dictionary_display_name(dict_path_or_dicrc: str) -> Optional[str]:
    if not dict_path_or_dicrc or not os.path.exists(dict_path_or_dicrc):
        return None

    try:
        if (
            os.path.isfile(dict_path_or_dicrc)
            and os.path.basename(dict_path_or_dicrc).lower() == "dicrc"
        ):
            dict_dir = os.path.dirname(dict_path_or_dicrc)
        elif os.path.isdir(dict_path_or_dicrc):
            dict_dir = dict_path_or_dicrc
        elif os.path.isfile(dict_path_or_dicrc):
            dict_dir = os.path.dirname(dict_path_or_dicrc)
        else:
            return None

        readme_path = None
        for filename in os.listdir(dict_dir):
            if filename.lower().startswith("readme") and os.path.isfile(
                os.path.join(dict_dir, filename)
            ):
                readme_path = os.path.join(dict_dir, filename)
                break

        if readme_path:
            with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    dict_name_line = lines[1].strip()
                    if dict_name_line:
                        if (
                            re.match(r"^[vV]?\d+\.\d+", dict_name_line)
                            or "date:" in dict_name_line.lower()
                        ):
                            if lines[0].strip():
                                return lines[0].strip()
                        return dict_name_line
                    elif lines[0].strip():
                        return lines[0].strip()
                elif len(lines) == 1 and lines[0].strip():
                    return lines[0].strip()
    except Exception as e:
        logging.error(
            f"Error while getting dictionary name for path '{dict_path_or_dicrc}': {e}"
        )

    if os.path.isdir(dict_path_or_dicrc):
        return os.path.basename(os.path.normpath(dict_path_or_dicrc))
    elif os.path.isfile(dict_path_or_dicrc):
        return os.path.basename(os.path.normpath(os.path.dirname(dict_path_or_dicrc)))
    return None


def create_empty_metadata(
    surface: str, start_pos_orig: int, length_orig: int, is_sentence_start: bool
) -> Dict:
    chj_start = 10 + start_pos_orig * 10
    chj_end = 10 + (start_pos_orig + length_orig) * 10

    return {
        "file_name": "",
        "subcorpus_name": "",
        "start_position": chj_start,
        "end_position": chj_end,
        "sentence_boundary": ("B" if is_sentence_start else "I"),
        "surface_form": surface,
        "lexeme": surface,
        "lexeme_reading": "",
        "pos": "不明",
        "conjugation_type": "",
        "conjugation_form": "",
        "pronunciation": "",
        "word_type": "",
    }


def format_pos(features: list) -> str:
    pos_parts = []
    for i in range(min(4, len(features))):
        if features[i] not in ["", "*"]:
            pos_parts.append(features[i])
    return "-".join(pos_parts) if pos_parts else "不明"


def csv_escape(value: str) -> str:
    if not isinstance(value, str):
        value = str(value)
    if '"' in value or "," in value or "\n" in value or "\r" in value:
        escaped_value = value.replace('"', '""')
        return f'"{escaped_value}"'
    return value
