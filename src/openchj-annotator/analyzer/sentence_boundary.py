import re
from typing import Dict, List, Optional, Tuple

DEFAULT_SENTENCE_BOUNDARY_SETTINGS = {
    "end_punct": "。",
    "end_quote": "設定なし",
    "use_explicit_marker": False,
}


def strip_explicit_boundary_markers(
    text: str, marker: str = "[B]"
) -> Tuple[str, List[int]]:
    if not text or marker not in text:
        return text, []

    positions: List[int] = []
    parts: List[str] = []
    scan_index = 0
    current_len = 0

    while True:
        marker_index = text.find(marker, scan_index)
        if marker_index == -1:
            parts.append(text[scan_index:])
            break

        chunk = text[scan_index:marker_index]
        parts.append(chunk)
        current_len += len(chunk)
        positions.append(current_len)
        scan_index = marker_index + len(marker)

    return "".join(parts), positions


def _get_boundary_settings(settings: Optional[Dict]) -> Tuple[set, set]:
    settings = settings or {}
    end_punct_setting = settings.get(
        "end_punct", DEFAULT_SENTENCE_BOUNDARY_SETTINGS["end_punct"]
    )
    end_quote_setting = settings.get(
        "end_quote", DEFAULT_SENTENCE_BOUNDARY_SETTINGS["end_quote"]
    )

    punct_map = {
        "設定なし": set(),
        "。": {"。"},
        "。, ？": {"。", "？"},
        "。, ？, ！": {"。", "？", "！"},
    }
    quote_map = {
        "設定なし": set(),
        "」": {"」"},
        "』": {"』"},
        "」, 』": {"」", "』"},
    }

    end_punct_set = punct_map.get(end_punct_setting, set())
    end_quote_set = quote_map.get(end_quote_setting, set())
    return end_punct_set, end_quote_set


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    sentences = re.split(r"(?<=[。．？！])\s*", text)
    return [s for s in sentences if s]


def adjust_sentence_boundaries(
    tokens: List[Dict],
    settings: Optional[Dict] = None,
    explicit_boundary_positions: Optional[List[int]] = None,
) -> List[Dict]:
    if not tokens:
        return tokens

    end_punct_set, end_quote_set = _get_boundary_settings(settings)

    for token_idx, token in enumerate(tokens):
        token["sentence_boundary"] = "I" if token_idx > 0 else "B"
        token.setdefault("surface_form", "")

    if len(tokens) <= 1:
        return tokens

    for i in range(len(tokens) - 1):
        current_token_surface = tokens[i]["surface_form"]
        next_token_surface = tokens[i + 1]["surface_form"]

        if current_token_surface in end_punct_set:
            if next_token_surface in end_quote_set:
                tokens[i + 1]["sentence_boundary"] = "I"
                if (i + 2) < len(tokens):
                    tokens[i + 2]["sentence_boundary"] = "B"
            else:
                tokens[i + 1]["sentence_boundary"] = "B"
        elif current_token_surface in end_quote_set:
            tokens[i + 1]["sentence_boundary"] = "B"

    if explicit_boundary_positions:
        explicit_boundary_positions = sorted(set(explicit_boundary_positions))
        for boundary_pos in explicit_boundary_positions:
            for token in tokens:
                token_start = token.get("_original_char_start")
                token_end = token.get("_original_char_end")
                if token_start is None or token_end is None:
                    continue
                if token_start <= boundary_pos < token_end:
                    token["sentence_boundary"] = "B"
                    break
                if boundary_pos < token_start:
                    token["sentence_boundary"] = "B"
                    break

    return tokens
