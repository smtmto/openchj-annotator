import logging
import os
from typing import Dict, List, Optional, Tuple

import fugashi
from utils.file_utils import (get_downloads_directory, read_text_file,
                              replace_datetime_placeholder, write_text_file)
from utils.tag_processor import TagProcessor

from config import Config

from .analyzer_utils import (format_pos, get_dictionary_display_name,
                             load_jis_mapping)
from .preprocessor import (apply_text_formatting_for_display,
                           get_format_settings)
from .sentence_boundary import adjust_sentence_boundaries


class OpenCHJAnnotator:
    CHJ_POSITION_MULTIPLIER = 10

    def __init__(self, config=None):
        os.environ.pop("MECABRC", None)
        self.config = config or Config()
        self.tagger = self._initialize_tagger()
        self.jis_mapping = load_jis_mapping()
        tag_special_settings_from_conf = self.config.config.get(
            "tag_special_settings", {}
        )
        self.tag_processor = TagProcessor(tag_special_settings_from_conf)
        self._parallel_warning_shown = False

    def _initialize_tagger(self) -> fugashi.Tagger:
        active_dict = self.config.get_active_dictionary()
        dict_path = self.config.get_unidic_path(active_dict)
        user_dict_path = (
            None if active_dict == "lite" else self.config.get_user_dictionary_path()
        )
        self.user_dict_incompatible = False

        rc_option = "-r NUL" if os.name == "nt" else "-r /dev/null"

        try:
            if active_dict == "lite" or dict_path is None or dict_path == "bundled":
                try:
                    tagger_options_lite = rc_option
                    tagger = fugashi.Tagger(tagger_options_lite)
                    try:
                        tagger("テスト文章です")
                    except Exception as e:
                        logging.warning(f"UniDic-lite test error: {e}")
                    return tagger
                except Exception as e:
                    logging.error(f"UniDic-lite initialization failed: {e}")
                    try:
                        return fugashi.Tagger(rc_option)
                    except Exception as e_fallback_rc:
                        logging.warning(
                            f"Fallback fugashi.Tagger(rc_option) failed: {e_fallback_rc}, trying without options."
                        )
                        try:
                            return fugashi.Tagger()
                        except Exception as e_fallback_final:
                            logging.critical(
                                f"Default fugashi.Tagger() initialization failed: {e_fallback_final}"
                            )
                            raise RuntimeError(
                                "Failed to initialize morphological analyzer."
                            ) from e_fallback_final
            else:
                system_dict_option_part = ""

                if os.path.isdir(dict_path):
                    dict_path_mecab = self._get_platform_specific_path(
                        dict_path, for_mecab=True
                    )
                    system_dict_option_part = f'-d "{dict_path_mecab}"'
                elif (
                    os.path.isfile(dict_path)
                    and os.path.basename(dict_path).lower() == "dicrc"
                ):
                    dict_dir = os.path.dirname(dict_path)
                    dict_dir_mecab = self._get_platform_specific_path(
                        dict_dir, for_mecab=True
                    )
                    system_dict_option_part = f'-d "{dict_dir_mecab}"'
                elif os.path.isfile(dict_path):
                    dict_dir = os.path.dirname(dict_path)
                    dict_dir_mecab = self._get_platform_specific_path(
                        dict_dir, for_mecab=True
                    )
                    system_dict_option_part = f'-d "{dict_dir_mecab}"'
                else:
                    raise FileNotFoundError(
                        f"Specified system dictionary path not found: {dict_path}"
                    )

                options_system_only = f"{rc_option} {system_dict_option_part}".strip()

                user_dict_option_part = ""
                if user_dict_path and os.path.exists(user_dict_path):
                    user_dict_mecab = self._get_platform_specific_path(
                        user_dict_path, for_mecab=True
                    )
                    user_dict_extension = os.path.splitext(user_dict_path)[1].lower()
                    if user_dict_extension != ".dic":
                        logging.warning(
                            f"User dictionary extension is not .dic: {user_dict_path}"
                        )
                    user_dict_option_part = f'-u "{user_dict_mecab}"'

                options_with_user_dict = f"{rc_option} {system_dict_option_part} {user_dict_option_part}".strip()

                if user_dict_option_part:
                    try:
                        tagger = fugashi.Tagger(options_with_user_dict)
                        tagger("テスト文章です")
                        self.user_dict_incompatible = False
                        return tagger
                    except Exception as e_user_dict:
                        error_msg = str(e_user_dict)
                        logging.warning(
                            f"Tagger initialization with user dictionary failed ('{options_with_user_dict}'): {e_user_dict}"
                        )
                        if "incompatible dictionary" in error_msg:
                            self.user_dict_incompatible = True
                            logging.warning(
                                f"User dictionary '{user_dict_path}' is incompatible with system dictionary '{dict_path}'."
                            )
                try:
                    tagger = fugashi.Tagger(options_system_only)
                    tagger("テスト文章です")
                    return tagger
                except Exception as e_system_only:
                    logging.warning(
                        f"Tagger initialization with system dictionary only also failed ('{options_system_only}'): {e_system_only}"
                    )
                    if user_dict_option_part and self.user_dict_incompatible:
                        logging.error(
                            f"Failed with user dict (incompatible), and also failed with system dict only. System dict: {dict_path}"
                        )
                    else:
                        logging.error(
                            f"Failed with system dict only. System dict: {dict_path}"
                        )
                    return fugashi.Tagger(rc_option)

        except FileNotFoundError as e_fnf:
            logging.error(f"Dictionary path error: {e_fnf}")
            return fugashi.Tagger(rc_option)
        except Exception as e_outer:
            logging.critical(f"Outer Tagger initialization failed: {e_outer}")
            return fugashi.Tagger(rc_option)

    def get_current_dictionary_name(self) -> str:
        if hasattr(self, "tagger") and self.tagger:
            try:
                active_dict = self.config.get_active_dictionary()
                if active_dict == "lite":
                    return "UniDic-lite (デフォルト)"
                else:
                    dict_path = self.config.get_unidic_path(active_dict)
                    display_name = "カスタム辞書"
                    if dict_path:
                        readme_name = get_dictionary_display_name(dict_path)
                        if readme_name:
                            display_name = readme_name
                        else:
                            display_name = f"カスタム辞書 ({os.path.basename(os.path.normpath(dict_path))})"
                    user_dict_path = self.config.get_user_dictionary_path()
                    if user_dict_path and os.path.exists(user_dict_path):
                        user_dict_name = os.path.basename(user_dict_path)
                        if (
                            hasattr(self, "user_dict_incompatible")
                            and self.user_dict_incompatible
                        ):
                            logging.warning(
                                f"User dictionary is incompatible and will not be used: {user_dict_name}"
                            )
                            return f"{display_name} (User dictionary incompatibility: {user_dict_name})"
                        else:
                            return f"{display_name} (User dictionary: {user_dict_name})"
                    else:
                        return display_name
            except Exception:
                return "Dictionary name retrieval error"
        return "Analyzer not initialized"

    def _create_morph_token_dict_from_node(
        self, token: fugashi.UnidicNode, position: int = 0
    ) -> Dict:
        try:
            features = token.feature_raw.split(",")
            num_features = len(features)

            def get_feature(index, default=""):
                return (
                    features[index]
                    if index < num_features and features[index] != "*"
                    else default
                )

            original_char_start = position
            original_char_end = position + len(token.surface)

            metadata = {
                "surface_form": token.surface,
                "lexeme": get_feature(7, token.surface),
                "lexeme_reading": get_feature(6, ""),
                "pos": format_pos(features),
                "conjugation_type": get_feature(4, ""),
                "conjugation_form": get_feature(5, ""),
                "pronunciation": get_feature(9, ""),
                "word_type": get_feature(12, ""),
                "_original_char_start": original_char_start,
                "_original_char_end": original_char_end,
                "_is_special_tag": False,
                "sentence_boundary": "I",
            }
            return metadata
        except Exception as e:
            surface_info = "UnknownSurface"
            if hasattr(token, "surface"):
                surface_info = token.surface

            logging.error(f"Morph token creation error (Token: '{surface_info}'): {e}")
            import traceback

            logging.error(traceback.format_exc())

            return {
                "surface_form": surface_info,
                "lexeme": surface_info,
                "_original_char_start": position,
                "_original_char_end": position + len(surface_info),
                "_is_special_tag": False,
                "pos": "不明",
                "sentence_boundary": "I",
            }

    def _create_special_token_dict(
        self,
        pattern_config: Dict,
        content_original_char_start: int,
    ) -> Dict:
        surface_form = pattern_config.get("surface_form", "")

        content_original_char_end = content_original_char_start + len(surface_form)

        metadata = {
            "surface_form": surface_form,
            "lexeme": pattern_config.get("lexeme", surface_form),
            "lexeme_reading": pattern_config.get("lexeme_reading", ""),
            "pos": pattern_config.get("pos_value", "不明-特別タグ"),
            "conjugation_type": pattern_config.get("conjugation_type", ""),
            "conjugation_form": pattern_config.get("conjugation_form", ""),
            "pronunciation": pattern_config.get("pronunciation", ""),
            "word_type": pattern_config.get("word_type", ""),
            "_original_char_start": content_original_char_start,
            "_original_char_end": content_original_char_end,
            "_is_special_tag": True,
            "sentence_boundary": "I",
        }
        return metadata

    def _find_special_tag_sequences(
        self, fugashi_tokens: List[fugashi.UnidicNode], tag_special_patterns: List[Dict]
    ) -> List[Tuple[int, int, Dict]]:
        identified_sequences = []

        def get_bracket_chars_for_pattern(bracket_type_str: str) -> Tuple[str, str]:
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
            return brackets_map.get(bracket_type_str, ("", ""))

        n_tokens = len(fugashi_tokens)
        potential_matches = []

        for pattern_config in tag_special_patterns:
            start_bracket_char, end_bracket_char = get_bracket_chars_for_pattern(
                pattern_config.get("bracket_type", "")
            )
            tag_key = pattern_config.get("tag_content", "")
            expected_surface = pattern_config.get("surface_form", "")

            if not all(
                [start_bracket_char, end_bracket_char, tag_key, expected_surface]
            ):
                logging.warning(
                    f"Skipping incomplete special tag pattern: {pattern_config}"
                )
                continue

            for i in range(n_tokens):

                if fugashi_tokens[i].surface == start_bracket_char:
                    current_idx = i + 1

                    key_tokens_surfaces = []
                    key_match_end_idx = -1

                    temp_key_idx = current_idx
                    accumulated_key_surface = ""
                    while temp_key_idx < n_tokens and len(
                        accumulated_key_surface
                    ) < len(tag_key):
                        accumulated_key_surface += fugashi_tokens[temp_key_idx].surface
                        key_tokens_surfaces.append(fugashi_tokens[temp_key_idx].surface)
                        temp_key_idx += 1
                        if accumulated_key_surface == tag_key:
                            key_match_end_idx = temp_key_idx - 1
                            break

                    if key_match_end_idx == -1:
                        continue

                    current_idx = key_match_end_idx + 1

                    if (
                        current_idx < n_tokens
                        and fugashi_tokens[current_idx].surface == ":"
                    ):
                        current_idx += 1

                        if (
                            current_idx < n_tokens
                            and fugashi_tokens[current_idx].surface == " "
                        ):
                            current_idx += 1

                    content_tokens_surfaces = []
                    content_match_end_idx = -1
                    accumulated_content_surface = ""

                    temp_content_idx = current_idx

                    while temp_content_idx < n_tokens:
                        token_surf = fugashi_tokens[temp_content_idx].surface

                        if token_surf == end_bracket_char:
                            break

                        next_accumulated_content_surface = (
                            accumulated_content_surface + token_surf
                        )

                        if expected_surface.startswith(
                            next_accumulated_content_surface
                        ) or next_accumulated_content_surface.startswith(
                            expected_surface
                        ):

                            accumulated_content_surface = (
                                next_accumulated_content_surface
                            )
                            content_tokens_surfaces.append(token_surf)

                            normalized_accumulated = "".join(
                                accumulated_content_surface.split()
                            )
                            normalized_expected = "".join(expected_surface.split())

                            if normalized_accumulated == normalized_expected:
                                content_match_end_idx = temp_content_idx
                                break
                        else:
                            break

                        temp_content_idx += 1

                    if content_match_end_idx == -1:
                        continue

                    current_idx = content_match_end_idx + 1

                    if (
                        current_idx < n_tokens
                        and fugashi_tokens[current_idx].surface == end_bracket_char
                    ):

                        potential_matches.append((i, current_idx, pattern_config))

        potential_matches.sort(key=lambda x: (x[0], -(x[1] - x[0])))

        last_tag_end_idx = -1
        for start_idx, end_idx, config in potential_matches:
            if start_idx > last_tag_end_idx:
                identified_sequences.append((start_idx, end_idx, config))
                last_tag_end_idx = end_idx

        return identified_sequences

    def analyze(
        self, text: str, temp_format_settings: Optional[Dict] = None
    ) -> List[Dict]:
        current_format_settings = get_format_settings(self.config, temp_format_settings)

        text_formatted_for_fugashi = apply_text_formatting_for_display(
            text,
            current_format_settings,
            self.jis_mapping,
        )
        try:
            fugashi_output_iterable = self.tagger(text_formatted_for_fugashi)
            fugashi_nodes = list(fugashi_output_iterable)

        except Exception as e:
            logging.error(f"Fugashi parsing (formatted text) failed: {e}")
            import traceback

            logging.error(traceback.format_exc())
            return []

        tag_special_patterns = current_format_settings.get(
            "tag_special_settings", {}
        ).get("tag_patterns", [])

        special_tag_sequences = self._find_special_tag_sequences(
            fugashi_nodes, tag_special_patterns
        )

        all_tokens_raw: List[Dict] = []
        current_position_in_formatted_text = 0
        fugashi_node_idx = 0
        special_tag_info_idx = 0
        special_tag_sequences.sort(key=lambda x: x[0])

        while fugashi_node_idx < len(fugashi_nodes):
            current_node_is_start_of_a_special_tag = False
            tag_to_process_this_iteration = None

            if special_tag_info_idx < len(special_tag_sequences):
                next_special_tag_start_node_idx, _end_idx, _config = (
                    special_tag_sequences[special_tag_info_idx]
                )
                if fugashi_node_idx == next_special_tag_start_node_idx:
                    current_node_is_start_of_a_special_tag = True
                    tag_to_process_this_iteration = special_tag_sequences[
                        special_tag_info_idx
                    ]

            if (
                current_node_is_start_of_a_special_tag
                and tag_to_process_this_iteration is not None
            ):
                tag_start_node_idx, tag_end_node_idx, tag_pattern_config_from_find = (
                    tag_to_process_this_iteration
                )

                content_absolute_original_char_start = (
                    current_position_in_formatted_text
                )

                special_token_dict = self._create_special_token_dict(
                    tag_pattern_config_from_find,
                    content_absolute_original_char_start,
                )

                if special_token_dict:
                    all_tokens_raw.append(special_token_dict)

                if special_token_dict and "_original_char_end" in special_token_dict:
                    current_position_in_formatted_text = special_token_dict[
                        "_original_char_end"
                    ]
                else:
                    logging.error(
                        "  CRITICAL: special_token_dict is invalid for special tag!"
                    )
                    current_position_in_formatted_text += len(
                        tag_pattern_config_from_find.get("surface_form", "")
                    )

                fugashi_node_idx = tag_end_node_idx + 1
                special_tag_info_idx += 1

            else:
                if fugashi_node_idx >= len(fugashi_nodes):
                    break
                node = fugashi_nodes[fugashi_node_idx]

                morph_token_original_char_start = current_position_in_formatted_text
                morph_token_dict = self._create_morph_token_dict_from_node(
                    node, morph_token_original_char_start
                )

                if node.surface and node.surface.strip():
                    if morph_token_dict:
                        all_tokens_raw.append(morph_token_dict)

                consumed_length_by_morph = len(node.surface)
                if hasattr(node, "white_space") and node.white_space:
                    consumed_length_by_morph += len(node.white_space)

                current_position_in_formatted_text += consumed_length_by_morph
                fugashi_node_idx += 1

        final_tokens_with_chj: List[Dict] = []
        processed_tokens_count_for_chj = 0
        chj_current_start_position_tracker = self.CHJ_POSITION_MULTIPLIER

        for token_dict_raw in all_tokens_raw:
            if (
                "_original_char_start" not in token_dict_raw
                or "_original_char_end" not in token_dict_raw
            ):
                logging.warning(
                    f"Skipping token due to missing original positions (formatted text): {token_dict_raw.get('surface_form')}"
                )
                continue

            orig_start_formatted = token_dict_raw["_original_char_start"]
            orig_end_formatted = token_dict_raw["_original_char_end"]
            content_length_formatted_chars = orig_end_formatted - orig_start_formatted

            current_token_chj_start = chj_current_start_position_tracker
            current_token_chj_end = current_token_chj_start + (
                content_length_formatted_chars * self.CHJ_POSITION_MULTIPLIER
            )

            token_dict_raw["start_position"] = current_token_chj_start
            token_dict_raw["end_position"] = current_token_chj_end

            chj_current_start_position_tracker = current_token_chj_end

            token_dict_raw.setdefault("file_name", "")
            token_dict_raw.setdefault("subcorpus_name", "")
            final_tokens_with_chj.append(token_dict_raw)
            processed_tokens_count_for_chj += 1

        final_tokens_adjusted_boundary = adjust_sentence_boundaries(
            final_tokens_with_chj
        )

        for token in final_tokens_adjusted_boundary:
            token.pop("_original_char_start", None)
            token.pop("_original_char_end", None)
            token.pop("_is_special_tag", None)

        return final_tokens_adjusted_boundary

    def analyze_parallel(
        self,
        text: str,
        _num_workers: int = None,
        temp_format_settings: Optional[Dict] = None,
    ) -> List[Dict]:
        if not self._parallel_warning_shown:
            logging.warning(
                "analyze_parallel is using single-threaded analyze due to significant "
                "changes in the analysis pipeline. Parallel processing needs to be re-evaluated."
            )
            self._parallel_warning_shown = True
        return self.analyze(text, temp_format_settings)

    def preprocess_text_with_tag_info(
        self, text: str, temp_format_settings: Optional[Dict] = None
    ) -> Tuple[str, List[Dict]]:
        if not text or not text.strip():
            return "", []

        current_format_settings = get_format_settings(self.config, temp_format_settings)

        tag_special_config_for_tp = current_format_settings.get(
            "tag_special_settings", {}
        )
        _original_text_ref, detected_tags_for_highlight_on_original = (
            self.tag_processor.process_text(text, temp_config=tag_special_config_for_tp)
        )

        text_for_display_formatted = apply_text_formatting_for_display(
            text, current_format_settings, self.jis_mapping
        )

        return text_for_display_formatted, detected_tags_for_highlight_on_original

    def preprocess_text(
        self, text: str, temp_format_settings: Optional[Dict] = None
    ) -> str:
        logging.warning(
            "OpenCHJAnnotator.preprocess_text (class method) is now returning fully formatted text for display/preview purposes."
        )
        current_format_settings = get_format_settings(self.config, temp_format_settings)
        return apply_text_formatting_for_display(
            text, current_format_settings, self.jis_mapping
        )

    def _get_platform_specific_path(self, path: str, for_mecab: bool = True) -> str:
        if not path:
            return path
        if for_mecab and os.name == "nt":
            return path.replace("/", "\\")
        else:
            return path.replace("\\", "/")

    def format_as_tsv(self, results: List[Dict], filename: str = "unknown.txt") -> str:
        from .formatter import format_as_tsv as format_tsv_external

        return format_tsv_external(results, filename, self.config)

    def format_as_csv(self, results: List[Dict], filename: str = "unknown.txt") -> str:
        from .formatter import format_as_csv as format_csv_external

        return format_csv_external(results, filename, self.config)

    def format_as_json(self, results: List[Dict], filename: str = "unknown.txt") -> str:
        from .formatter import format_as_json as format_json_external

        return format_json_external(results, filename, self.config)

    def analyze_file(self, input_path: str, output_path: str = None) -> str:
        try:
            text = read_text_file(input_path)
            results = self.analyze(text)
            output_settings = self.config.config.get("output_settings", {})
            encoding = "utf-8"

            if output_path is None:
                prefix = output_settings.get("prefix", "")
                suffix = output_settings.get("suffix", "_analyzed")
                suffix = replace_datetime_placeholder(suffix)
                use_custom_dir = output_settings.get("use_custom_output_dir", False)
                output_dir_base = (
                    output_settings.get(
                        "output_directory" if use_custom_dir else "default_directory",
                        "",
                    )
                    or get_downloads_directory()
                )
                os.makedirs(output_dir_base, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(
                    output_dir_base, f"{prefix}{base_name}{suffix}.txt"
                )

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            content = self.format_as_tsv(results, os.path.basename(input_path))
            write_text_file(content, output_path, encoding=encoding)
            return output_path
        except FileNotFoundError:
            logging.error(f"Input file is not found: {input_path}")
            raise
        except Exception as e:
            logging.error(
                f"Error occurred while analyzing or writing file: '{input_path}': {e}"
            )
            raise
