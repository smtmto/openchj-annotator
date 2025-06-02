import logging
import re
from typing import Dict, Optional

from .analyzer_utils import jis_to_unicode


def process_aozora_annotations_for_display(
    text: str, jis_mapping: Dict[str, str]
) -> str:
    processed_text = text

    def replace_jis_character_in_note(match):
        note_content = match.group(0)
        jis_code_search = re.search(r"(第\d水準\d+-\d+-\d+)", note_content)
        if jis_code_search:
            jis_code_str = jis_code_search.group(1)
            unicode_char = jis_to_unicode(jis_code_str, jis_mapping)
            if unicode_char:
                return unicode_char
        return ""

    processed_text = re.sub(
        r"※?［＃[^］]*?(第\d水準\d+-\d+-\d+)[^］]*?］",
        replace_jis_character_in_note,
        processed_text,
    )
    processed_text = re.sub(
        r"([^｜《》]+?)｜([^｜《》]+?)《[^《》]*?》", r"\1\2", processed_text
    )
    processed_text = re.sub(r"《[^《》]*?》", "", processed_text)
    processed_text = re.sub(r"［＃[^］]*?］", "", processed_text)
    processed_text = re.sub(r"〔.*?〕", "", processed_text)

    return processed_text


def aozora_cleanup_for_display(text: str, jis_mapping: Dict[str, str]) -> str:
    cleaned_text = text
    parts = re.split(r"^-{5,}.*?-{5,}$", cleaned_text, flags=re.MULTILINE)
    if len(parts) >= 3:
        cleaned_text = parts[0].rstrip() + "\n\n" + parts[2].lstrip()
    elif len(parts) == 2 and parts[0].strip() == "":
        cleaned_text = parts[1].lstrip()
    elif len(parts) == 2 and parts[1].strip() == "":
        cleaned_text = parts[0].rstrip()
    cleaned_text = re.split(r"^底本：", cleaned_text, maxsplit=1, flags=re.MULTILINE)[0]
    cleaned_text = process_aozora_annotations_for_display(cleaned_text, jis_mapping)
    return cleaned_text.strip()


def get_format_settings(config, temp_format_settings: Optional[Dict] = None) -> Dict:
    settings = {}
    base_config_dict = config.config if config else {}

    default_tag_settings = {
        "enabled": False,
        "types": [],
        "mode": "remove_with_content",
    }
    default_regex_settings = {"enabled": False, "patterns": []}
    default_output_settings = {
        "remove_half_space": False,
        "remove_full_space": False,
        "remove_newline": False,
    }
    default_aozora_cleanup = False
    default_tag_special_settings = {"tag_patterns": []}

    tag_s = base_config_dict.get("remove_tags", default_tag_settings.copy())
    regex_s = base_config_dict.get("regex_settings", default_regex_settings.copy())
    output_s_base = base_config_dict.get(
        "output_settings", default_output_settings.copy()
    )
    aozora_s = base_config_dict.get("aozora_cleanup", default_aozora_cleanup)
    tag_special_s = base_config_dict.get(
        "tag_special_settings", default_tag_special_settings.copy()
    )

    if temp_format_settings is not None:
        tag_s = temp_format_settings.get("remove_tags", tag_s)
        regex_s = temp_format_settings.get("regex_settings", regex_s)
        ws_temp = temp_format_settings.get("whitespace_settings")
        if ws_temp is not None:
            output_s_base = ws_temp
        aozora_s = temp_format_settings.get("aozora_cleanup", aozora_s)
        tag_special_s = temp_format_settings.get("tag_special_settings", tag_special_s)

    settings["tag_settings"] = tag_s
    settings["regex_settings"] = regex_s
    settings["output_settings"] = output_s_base
    settings["aozora_cleanup"] = aozora_s
    settings["tag_special_settings"] = tag_special_s

    return settings


def apply_text_formatting_for_display(
    text: str,
    format_settings: Dict,
    jis_mapping: Dict[str, str],
) -> str:
    formatted_text = text

    if format_settings.get("aozora_cleanup", False):
        formatted_text = aozora_cleanup_for_display(formatted_text, jis_mapping)

    tag_s = format_settings.get("tag_settings", {})
    if tag_s.get("enabled", False):
        types_to_remove_from_ui = set(tag_s.get("types", []))
        mode = tag_s.get("mode", "remove_with_content")

        special_tag_patterns_config = format_settings.get(
            "tag_special_settings", {}
        ).get("tag_patterns", [])
        special_bracket_types_used_in_special = {
            p.get("bracket_type")
            for p in special_tag_patterns_config
            if p.get("bracket_type")
        }

        ui_key_to_special_bracket_type_map = {
            "<>": "angle",
            "()": "round",
            "[]": "square",
            "{}": "curly",
            "＜＞": "angle_full",
            "（）": "round_full",
            "［］": "square_full",
            "｛｝": "curly_full",
            "【】": "corner",
            "《》": "double_angle_ja",
        }

        types_to_actually_remove = set()
        for ui_tag_key in types_to_remove_from_ui:
            corresponding_special_type = ui_key_to_special_bracket_type_map.get(
                ui_tag_key
            )
            if (
                corresponding_special_type
                and corresponding_special_type in special_bracket_types_used_in_special
            ):
                continue
            types_to_actually_remove.add(ui_tag_key)

        bracket_map_internal = {
            "<>": ("<", ">"),
            "()": ("(", ")"),
            "[]": ("[", "]"),
            "{}": ("{", "}"),
            "【】": ("【", "】"),
            "《》": ("《", "》"),
            "＜＞": ("＜", "＞"),
            "（）": ("（", "）"),
            "［］": ("［", "］"),
            "｛｝": ("｛", "｝"),
            "〈〉": ("〈", "〉"),
        }

        for tag_type_key_to_remove in types_to_actually_remove:
            b_open, b_close = bracket_map_internal.get(
                tag_type_key_to_remove, (None, None)
            )
            if b_open and b_close:
                try:
                    pattern_str_tag = f"{re.escape(b_open)}.*?{re.escape(b_close)}"
                    if mode == "remove_with_content":
                        formatted_text = re.sub(pattern_str_tag, "", formatted_text)
                    elif mode == "remove_tags_only":

                        def repl_tags_only_local(match_obj):
                            content_with_tags = match_obj.group(0)
                            if len(content_with_tags) > len(b_open) + len(b_close):
                                return content_with_tags[len(b_open) : -len(b_close)]
                            return ""

                        formatted_text = re.sub(
                            pattern_str_tag, repl_tags_only_local, formatted_text
                        )
                except re.error as e:
                    logging.warning(
                        f"Error removing general tag ({tag_type_key_to_remove}): {e}"
                    )
            else:
                logging.warning(
                    f"Unknown tag type for general removal: {tag_type_key_to_remove}"
                )

    output_s = format_settings.get("output_settings", {})
    if output_s.get("remove_full_space", False):
        formatted_text = formatted_text.replace("　", "")
    if output_s.get("remove_half_space", False):
        formatted_text = formatted_text.replace(" ", "")
    if output_s.get("remove_newline", False):
        formatted_text = (
            formatted_text.replace("\r\n", "").replace("\n", "").replace("\r", "")
        )

    regex_s = format_settings.get("regex_settings", {})
    if regex_s.get("enabled", False):
        for pattern_data in regex_s.get("patterns", []):
            pattern_str = pattern_data.get("pattern")
            replacement = pattern_data.get("replacement", "")
            if pattern_str:
                try:
                    formatted_text = re.sub(pattern_str, replacement, formatted_text)
                except re.error as e:
                    logging.warning(
                        f"Error applying regex: {pattern_str} -> {replacement}. Error: {e}"
                    )

    return formatted_text
