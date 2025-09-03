import os
import re
from typing import Optional

JP_TO_EN_MAP = {
    "話し言葉": "csj",
    "書き言葉": "cwj",
    "中古和文": "chuko",
    "中世文語": "chusei-bungo",
    "中世口語": "chusei-kougo",
    "上代語": "jodai",
    "近代文語": "kindai-bungo",
    "近世文語": "kinsei-bungo",
    "近世江戸口語": "kinsei-edo",
    "近世上方口語": "kinsei-kamigata",
    "近代口語小説": "novel",
    "和歌": "waka",
}


def _generate_english_suffix_from_readme(readme_content: str) -> str:
    lines = readme_content.splitlines()
    if len(lines) < 2:
        return "unidic-unknown"

    dict_name_jp = lines[1].strip()
    version_str = ""
    m = re.search(r"ver\.?(\d{4})\.(\d{2})", dict_name_jp, re.IGNORECASE)
    if m:
        version_str = f"{m.group(1)}{m.group(2)}"

    is_gendai = "現代" in dict_name_jp
    is_full = "フルパッケージ" in dict_name_jp

    for jp, en in JP_TO_EN_MAP.items():
        if jp in dict_name_jp:
            if is_gendai:
                suffix = f"unidic-{en}-{version_str}"
                if is_full:
                    suffix += "_full"
                return suffix
            else:
                return f"unidic-{en}-v{version_str}"

    return "unidic-custom"


def _read_readme_for_dicrc(dicrc_path: str) -> Optional[str]:
    try:
        if not dicrc_path:
            return None
        dic_dir = os.path.dirname(dicrc_path)
        if not dic_dir or not os.path.isdir(dic_dir):
            return None
        for f in os.listdir(dic_dir):
            p = os.path.join(dic_dir, f)
            if f.upper().startswith("README") and os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as fh:
                    return fh.read()
    except Exception:
        pass
    return None


def get_dictionary_based_suffix(config) -> str:
    try:
        active = config.get_active_dictionary()
    except Exception:
        active = "lite"

    if active == "lite":
        return "_unidic-lite-1.0.8"

    try:
        dicrc = config.get_unidic_path("dic")
    except Exception:
        dicrc = None

    english = None
    readme = _read_readme_for_dicrc(dicrc) if dicrc else None
    if readme:
        english = _generate_english_suffix_from_readme(readme)
    if not english:
        english = "unidic-custom"

    base_suffix = f"_{english}" if not english.startswith("_") else english

    try:
        user_dict_path = config.get_user_dictionary_path()
        if user_dict_path and os.path.exists(user_dict_path):
            return f"{base_suffix}_ud"
    except Exception:
        pass

    return base_suffix
