import logging
import re
from typing import Any, Dict, List, Tuple


class TagProcessor:
    def __init__(self, config=None):
        self.config = config if config is not None else {}

    def load_config(self, config_data):
        self.config = config_data if config_data is not None else {}

    def save_config(self):
        return self.config.copy()

    def process_text(self, text: str, temp_config=None) -> Tuple[str, List[Dict[str, Any]]]:
        original_text = text
        detected_special_tags: List[Dict[str, Any]] = []

        config_to_use = temp_config if temp_config is not None else self.config

        if (
            not config_to_use
            or not isinstance(config_to_use, dict)
            or not config_to_use.get("tag_patterns")
        ):
            return original_text, []

        all_matches_with_config = []

        for pattern_idx, pattern_config in enumerate(config_to_use.get("tag_patterns", [])):
            if not isinstance(pattern_config, dict):
                logging.warning(
                    f"TagProcessor.process_text: Skipping invalid pattern_config (not a dict) at index {pattern_idx}."
                )
                continue

            bracket_type = pattern_config.get("bracket_type", "")
            tag_content_key = pattern_config.get("tag_content", "")

            surface_form_in_config = pattern_config.get("surface_form", "")

            if not all([bracket_type, tag_content_key, surface_form_in_config]):
                logging.warning(
                    f"TagProcessor.process_text: Skipping incomplete tag pattern (missing bracket, key, or surface_form): {pattern_config}"
                )
                continue

            start_bracket_char, end_bracket_char = self._get_bracket_chars(bracket_type)
            if not start_bracket_char or not end_bracket_char:
                logging.warning(
                    f"TagProcessor.process_text: Invalid bracket type '{bracket_type}' for pattern: {pattern_config}"
                )
                continue

            start_escaped = re.escape(start_bracket_char)
            end_escaped = re.escape(end_bracket_char)
            key_escaped = re.escape(tag_content_key)
            content_escaped = re.escape(surface_form_in_config)

            regex_variants = [
                rf"{start_escaped}{key_escaped}{content_escaped}{end_escaped}",
                rf"{start_escaped}{key_escaped}:{content_escaped}{end_escaped}",
                rf"{start_escaped}{key_escaped}:\s{content_escaped}{end_escaped}",
            ]

            for variant_idx, regex_pattern_str in enumerate(regex_variants):
                try:
                    regex_pattern = re.compile(regex_pattern_str)
                    for match in regex_pattern.finditer(original_text):
                        char_start, char_end = match.span()
                        original_tag_text_matched = match.group(0)

                        all_matches_with_config.append(
                            (
                                char_start,
                                char_end,
                                original_tag_text_matched,
                                surface_form_in_config,
                                pattern_config,
                            )
                        )
                except re.error as e:
                    logging.error(
                        f"TagProcessor.process_text: Regex error for pattern '{regex_pattern_str}': {e}"
                    )

        if not all_matches_with_config:
            return original_text, []

        all_matches_with_config.sort(key=lambda x: (x[0], -(x[1] - x[0])))

        non_overlapping_matches = []
        last_char_end = -1
        for match_data_tuple in all_matches_with_config:
            char_start, char_end, original_tag_text, sf_conf, p_config_lambda = match_data_tuple
            if char_start >= last_char_end:
                non_overlapping_matches.append(match_data_tuple)
                last_char_end = char_end

        for (
            char_start,
            char_end,
            original_tag_text,
            sf_from_config,
            p_config_final,
        ) in non_overlapping_matches:
            tag_details = {
                "original_char_start": char_start,
                "original_char_end": char_end,
                "original_tag_text": original_tag_text,
                "surface_form": sf_from_config,
                "pos": p_config_final.get("pos_value", "不明-特別タグ"),
                "lexeme": p_config_final.get("lexeme", sf_from_config),
                "lexeme_reading": p_config_final.get("lexeme_reading", ""),
                "conjugation_type": p_config_final.get("conjugation_type", ""),
                "conjugation_form": p_config_final.get("conjugation_form", ""),
                "pronunciation": p_config_final.get("pronunciation", ""),
                "word_type": p_config_final.get("word_type", ""),
            }
            detected_special_tags.append(tag_details)

        detected_special_tags.sort(key=lambda x: x["original_char_start"])
        return original_text, detected_special_tags

    def _get_bracket_chars(self, bracket_type: str) -> Tuple[str, str]:
        brackets_map = {
            "angle": ("<", ">"),
            "angle_full": ("＜", "＞"),
            "round": ("(", ")"),
            "round_full": ("（", "）"),
            "square": ("[", "]"),
            "square_full": ("［", "］"),
            "curly": ("{", "}"),
            "curly_full": ("｛", "｝"),
            "corner": ("【", "】"),
        }
        return brackets_map.get(bracket_type, ("", ""))
