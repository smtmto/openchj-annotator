import json
import os
from typing import Dict, List

from .analyzer_utils import csv_escape


def format_as_tsv(
    results: List[Dict], filename: str = "unknown.txt", config=None
) -> str:
    lines = []
    base_filename = os.path.basename(filename)
    base_filename = os.path.splitext(base_filename)[0]

    for result in results:
        result["file_name"] = base_filename
        subcorpus = ""
        if config:
            subcorpus = config.config.get("subcorpus_name", "")
        result["subcorpus_name"] = "-" if not subcorpus else subcorpus

        row = [
            result.get("file_name", base_filename),
            result.get("subcorpus_name", "-"),
            str(result.get("start_position", 0)),
            str(result.get("end_position", 0)),
            result.get("sentence_boundary", "I"),
            result.get("surface_form", ""),
            result.get("lexeme", ""),
            result.get("lexeme_reading", ""),
            result.get("pos", "不明"),
            result.get("conjugation_type", ""),
            result.get("conjugation_form", ""),
            result.get("pronunciation", ""),
            result.get("word_type", ""),
        ]
        lines.append("\t".join(map(str, row)))

    return "\n".join(lines) + "\n"


def format_as_csv(
    results: List[Dict], filename: str = "unknown.txt", config=None
) -> str:
    output_rows = []
    base_filename = os.path.basename(filename)
    base_filename = os.path.splitext(base_filename)[0]

    fields = [
        "file_name",
        "subcorpus_name",
        "start_position",
        "end_position",
        "sentence_boundary",
        "surface_form",
        "lexeme",
        "lexeme_reading",
        "pos",
        "conjugation_type",
        "conjugation_form",
        "pronunciation",
        "word_type",
    ]

    for result in results:
        result["file_name"] = base_filename
        subcorpus = ""
        if config:
            subcorpus = config.config.get("subcorpus_name", "")
        result["subcorpus_name"] = "-" if not subcorpus else subcorpus

        row_values = []
        for field in fields:
            if field == "start_position" or field == "end_position":
                row_values.append(str(result.get(field, 0)))
            elif field == "sentence_boundary":
                row_values.append(result.get(field, "I"))
            elif field == "pos":
                row_values.append(result.get(field, "不明"))
            else:
                row_values.append(result.get(field, ""))

        output_rows.append(",".join([csv_escape(cell) for cell in row_values]))

    return "\n".join(output_rows) + "\n"


def format_as_json(
    results: List[Dict], filename: str = "unknown.txt", config=None
) -> str:
    base_filename = os.path.basename(filename)
    base_filename = os.path.splitext(base_filename)[0]
    output_data = []

    for result_item in results:

        result_item["file_name"] = base_filename
        subcorpus = ""
        if config:
            subcorpus = config.config.get("subcorpus_name", "")
        result_item["subcorpus_name"] = "-" if not subcorpus else subcorpus

        result_item.setdefault("start_position", 0)
        result_item.setdefault("end_position", 0)
        result_item.setdefault("sentence_boundary", "I")
        result_item.setdefault("surface_form", "")
        result_item.setdefault("lexeme", result_item.get("surface_form", ""))
        result_item.setdefault("lexeme_reading", "")
        result_item.setdefault("pos", "不明")
        result_item.setdefault("conjugation_type", "")
        result_item.setdefault("conjugation_form", "")
        result_item.setdefault("pronunciation", "")
        result_item.setdefault("word_type", "")

        output_data.append(result_item)

    json_str = json.dumps(output_data, ensure_ascii=False, indent=2)
    return json_str.replace("\r\n", "\n") + "\n"
