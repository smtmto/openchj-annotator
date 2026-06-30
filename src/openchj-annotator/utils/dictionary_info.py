import os
import re
from typing import Optional

JP_TO_EN_MAP = {
    "近現代口語小説": "novel",
    "近代口語小説": "novel",
    "関西方言": "kansai",
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
    "旧仮名口語": "qkana",
    "和歌": "waka",
}


FOLDER_TO_JP_MAP = {
    "unidic-csj": "現代話し言葉UniDic",
    "unidic-cwj": "現代書き言葉UniDic",
    "unidic-d-kansai": "関西方言UniDic",
    "unidic-chuko": "中古和文UniDic",
    "unidic-chusei-bungo": "中世文語UniDic",
    "unidic-chusei-kougo": "中世口語UniDic",
    "unidic-jodai": "上代語UniDic",
    "unidic-kindai-bungo": "近代文語UniDic",
    "unidic-kinsei-bungo": "近世文語UniDic",
    "unidic-kinsei-edo": "近世江戸口語UniDic",
    "unidic-kinsei-kamigata": "近世上方口語UniDic",
    "unidic-novel": "近代口語小説UniDic",
    "unidic-qkana": "旧仮名口語UniDic",
    "unidic-waka": "和歌UniDic",
}


def _clean_readme_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^#+\s*", "", line)
    line = re.sub(r"^[\-*]\s*", "", line)
    return line.strip()


def _extract_version(text: str) -> str:
    m = re.search(r"ver\.?\s*(\d{4})\.(\d{2})", text, re.IGNORECASE)
    if m:
        return f"{m.group(1)}{m.group(2)}"
    m = re.search(r"v?(\d{6})(?!\d)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return ""


def _format_version(version_str: str) -> str:
    if len(version_str) == 6 and version_str.isdigit():
        return f"{version_str[:4]}.{version_str[4:]}"
    return version_str


def _extract_dictionary_name(readme_content: str) -> Optional[str]:
    for raw_line in readme_content.splitlines():
        line = _clean_readme_line(raw_line)
        if not line or line.lower().startswith(("http://", "https://")):
            continue
        if "readme" in line.lower() or "date:" in line.lower():
            continue
        if "UniDic" in line or any(jp in line for jp in JP_TO_EN_MAP):
            return line
    return None


def _find_readme_path_for_dicrc(dicrc_path: str) -> Optional[str]:
    if not dicrc_path:
        return None

    dic_dir = dicrc_path if os.path.isdir(dicrc_path) else os.path.dirname(dicrc_path)
    if not dic_dir or not os.path.isdir(dic_dir):
        return None

    for f in os.listdir(dic_dir):
        p = os.path.join(dic_dir, f)
        if f.upper().startswith("README") and os.path.isfile(p):
            return p
    return None


def _normalize_dictionary_folder_name(dicrc_path: str) -> str:
    if not dicrc_path:
        return ""
    path = os.path.normpath(dicrc_path)
    if os.path.isfile(path):
        path = os.path.dirname(path)
    return os.path.basename(path).lower()


def _guess_dictionary_name_from_path(dicrc_path: str) -> Optional[str]:
    folder_name = _normalize_dictionary_folder_name(dicrc_path)
    if not folder_name:
        return None
    if folder_name.startswith("unidic-novel"):
        version = _extract_version(folder_name)
        if version and int(version) >= 202512:
            return "近現代口語小説UniDic"
    for prefix, display_name in FOLDER_TO_JP_MAP.items():
        if folder_name.startswith(prefix):
            return display_name
    return None


def get_dictionary_metadata_from_readme(
    readme_content: str, dicrc_path: str = ""
) -> dict:
    dict_name_jp = _extract_dictionary_name(readme_content)
    if not dict_name_jp:
        dict_name_jp = _guess_dictionary_name_from_path(dicrc_path) or "カスタム辞書"

    version_source = readme_content or dicrc_path or dict_name_jp
    version_str = _extract_version(version_source)
    display_name = dict_name_jp
    if version_str and not re.search(r"ver\.?\s*\d", display_name, re.IGNORECASE):
        display_name = f"{display_name} ver. {_format_version(version_str)}"

    is_gendai = "現代話し言葉" in dict_name_jp or "現代書き言葉" in dict_name_jp
    is_full = "フルパッケージ" in dict_name_jp

    english_suffix = "unidic-custom"
    for jp, en in JP_TO_EN_MAP.items():
        if jp in dict_name_jp:
            if is_gendai:
                suffix = f"unidic-{en}-{version_str}" if version_str else f"unidic-{en}"
                if is_full:
                    suffix += "_full"
                english_suffix = suffix
            else:
                english_suffix = (
                    f"unidic-{en}-v{version_str}" if version_str else f"unidic-{en}"
                )
            break

    return {
        "display_name": display_name,
        "suffix": english_suffix,
        "version": version_str,
    }


def get_dictionary_metadata(dicrc_path: str) -> dict:
    readme = _read_readme_for_dicrc(dicrc_path)
    if readme:
        return get_dictionary_metadata_from_readme(readme, dicrc_path)

    dict_name_jp = _guess_dictionary_name_from_path(dicrc_path) or "カスタム辞書"
    version_str = _extract_version(dicrc_path or "")
    return get_dictionary_metadata_from_readme(
        f"{dict_name_jp} ver. {version_str}" if version_str else dict_name_jp,
        dicrc_path,
    )


def _generate_english_suffix_from_readme(readme_content: str) -> str:
    return get_dictionary_metadata_from_readme(readme_content).get(
        "suffix", "unidic-custom"
    )


def _read_readme_for_dicrc(dicrc_path: str) -> Optional[str]:
    try:
        if not dicrc_path:
            return None
        readme_path = _find_readme_path_for_dicrc(dicrc_path)
        if readme_path:
            with open(readme_path, "r", encoding="utf-8") as fh:
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

    english = "unidic-custom"
    if dicrc:
        english = get_dictionary_metadata(dicrc).get("suffix", "unidic-custom")

    base_suffix = f"_{english}" if not english.startswith("_") else english

    try:
        user_dict_path = config.get_user_dictionary_path()
        if user_dict_path and os.path.exists(user_dict_path):
            return f"{base_suffix}_ud"
    except Exception:
        pass

    return base_suffix
