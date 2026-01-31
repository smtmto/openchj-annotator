"""
Processor for Historical Recordings of the NDL (National Diet Library).

File format: {PID}_{speaker}_{title}.txt
Line format: U00001_R001: [N:(introduction)...]content

Processing:
1. Extract PID from filename
2. Extract utteranceId (U00001) and speakerId (R001) from each line
3. Return content with tags removed
4. Generate output filename: {PID}_{utteranceId}
"""

import re
from typing import Dict, List, Optional, Tuple


def extract_pid_from_filename(filename: str) -> Optional[str]:
    """
    Extract PID from NDL historical recording filename.

    Args:
        filename: Input filename (e.g., "1313676_大隈重信_講演：憲政に於ける世論の勢力（一）.txt")

    Returns:
        PID string (e.g., "1313676"), or None if extraction fails
    """
    base_name = filename
    if "." in filename:
        base_name = filename.rsplit(".", 1)[0]

    pattern = r"^(\d{6,7})_"
    match = re.match(pattern, base_name)

    if match:
        return match.group(1)
    return None


def parse_rekion_line(line: str) -> Tuple[Optional[str], Optional[str], str]:
    """
    Parse a line of historical recording data to extract utteranceId, speakerId, and content.

    Args:
        line: Input line (e.g., "U00001_R001: [N:(introduction)...]content text")

    Returns:
        Tuple of (utteranceId, speakerId, content text)
        Returns (None, None, original line) if parsing fails
    """
    pattern = r"^\s*(U\d{5})_(R\d{3}):\s*(.*)$"
    match = re.match(pattern, line)

    if match:
        utterance_id = match.group(1)
        speaker_id = match.group(2)
        content = match.group(3)
        return utterance_id, speaker_id, content
    return None, None, line


def preprocess_rekion_text(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Preprocess entire historical recording text.

    Args:
        text: Full input text

    Returns:
        Tuple of (processed text, list of utterance info)
        Utterance info format: [{"utteranceId": "U00001", "speakerId": "R001",
                                 "originalLineIndex": 0, "charStart": 0, "charEnd": 50}, ...]
    """
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized_text.split("\n")
    processed_lines = []
    utterance_info_list = []
    current_char_pos = 0

    for line_index, line in enumerate(lines):
        if not line.strip():
            processed_lines.append(line)
            current_char_pos += len(line) + 1
            continue

        utterance_id, speaker_id, content = parse_rekion_line(line)

        if utterance_id and speaker_id:
            line_start = current_char_pos
            line_end = current_char_pos + len(content)

            utterance_info_list.append(
                {
                    "utteranceId": utterance_id,
                    "speakerId": speaker_id,
                    "originalLineIndex": line_index,
                    "charStart": line_start,
                    "charEnd": line_end,
                }
            )
            processed_lines.append(content)
            current_char_pos += len(content) + 1
        else:
            processed_lines.append(line)
            current_char_pos += len(line) + 1

    processed_text = "\n".join(processed_lines)
    return processed_text, utterance_info_list


def find_utterance_id_for_token(
    token_char_start: int, utterance_info_list: List[Dict[str, str]]
) -> Optional[str]:
    """
    Find utteranceId for a token based on its character position.

    Args:
        token_char_start: Character start position of token in preprocessed text
        utterance_info_list: Utterance info returned by preprocess_rekion_text()

    Returns:
        Corresponding utteranceId, or None if not found
    """
    for info in utterance_info_list:
        char_start = info.get("charStart", 0)
        char_end = info.get("charEnd", 0)
        if char_start <= token_char_start < char_end:
            return info["utteranceId"]

    return None


def is_rekion_data(subcorpus_name: str) -> bool:
    """
    Check if subcorpus name indicates historical recording data.

    Args:
        subcorpus_name: Subcorpus name

    Returns:
        True if historical recording data
    """
    return subcorpus_name == "歴史的音源"
