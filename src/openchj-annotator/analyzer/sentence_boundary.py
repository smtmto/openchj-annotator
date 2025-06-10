import re
from typing import Dict, List


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    sentences = re.split(r"(?<=[。．？！])\s*", text)
    return [s for s in sentences if s]


def adjust_sentence_boundaries(tokens: List[Dict]) -> List[Dict]:
    if not tokens:
        return tokens

    for token_idx, token in enumerate(tokens):
        token["sentence_boundary"] = "I" if token_idx > 0 else "B"
        token.setdefault("surface_form", "")

    if len(tokens) <= 1:
        return tokens

    for i in range(len(tokens) - 1):
        current_token_surface = tokens[i]["surface_form"]
        next_token_surface = tokens[i + 1]["surface_form"]

        if current_token_surface == "。" or current_token_surface == "」":

            if current_token_surface == "。" and next_token_surface == "」":
                tokens[i + 1]["sentence_boundary"] = "I"
                if (i + 2) < len(tokens) and tokens[i + 2]["surface_form"] == "「":
                    tokens[i + 2]["sentence_boundary"] = "B"
            else:
                if current_token_surface == "。" and next_token_surface != "」":
                    tokens[i + 1]["sentence_boundary"] = "B"
                elif current_token_surface == "」":
                    tokens[i + 1]["sentence_boundary"] = "B"

    return tokens
