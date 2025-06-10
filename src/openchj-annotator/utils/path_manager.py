import sys
from pathlib import Path

_project_root = None
_is_frozen = False
_app_name = "OpenCHJAnnotator"
_app_author = ""


def initialize_paths(project_root_str, is_frozen=None):
    global _project_root, _is_frozen

    _project_root = Path(project_root_str).resolve()
    _is_frozen = is_frozen if is_frozen is not None else getattr(sys, "frozen", False)

    if _is_frozen:
        src_path = _project_root / "src"
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))


def get_project_root():
    global _project_root

    if _project_root is None:
        if getattr(sys, "frozen", False) or "__compiled__" in globals():
            _project_root = Path(sys.executable).parent
        else:
            _project_root = Path(__file__).resolve().parent.parent.parent

    return _project_root


def get_effective_config_file_path(filename="config.json"):
    if _is_frozen:
        import os

        if os.name == "nt":
            user_config_dir = (
                Path(
                    os.environ.get(
                        "LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local")
                    )
                )
                / "OpenCHJAnnotator"
            )
        else:
            user_config_dir = Path(os.path.expanduser("~/.config")) / "OpenCHJAnnotator"

        user_config_path = user_config_dir / filename

        if not user_config_path.exists():
            user_config_path.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                "unidic_paths": {"lite": "bundled", "dic": None},
                "user_dictionary_path": None,
                "active_dictionary": "lite",
                "output_format": "tsv",
                "output_encoding": "utf-8",
                "remove_tags": {
                    "enabled": False,
                    "types": [],
                    "mode": "remove_with_content",
                },
                "regex_settings": {"enabled": False, "patterns": []},
                "tag_special_settings": {"tag_patterns": []},
                "subcorpus_name": "",
                "regex_rules": [],
                "aozora_cleanup": False,
                "output_settings": {
                    "format": "TSV",
                    "prefix": "",
                    "suffix": "_analyzed",
                    "default_directory": "",
                    "output_directory": None,
                    "remove_full_space": False,
                    "remove_half_space": False,
                    "remove_newline": False,
                    "include_subfolders": False,
                    "use_custom_output_dir": False,
                },
                "output_newline": "\n",
            }
            import json

            with open(user_config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)

        return user_config_path
    else:
        root = get_project_root()
        config_path = root / "config" / filename

        if not config_path.exists():
            alt_path = root / filename
            if alt_path.exists():
                return alt_path

        return config_path


def get_user_config_file_path(filename="config.json"):
    return get_effective_config_file_path(filename)


def get_resources_path():
    if _is_frozen:
        if hasattr(sys, "_MEIPASS"):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(sys.executable).parent

        resources_path = base_path / "resources"


        if resources_path.exists():
            return resources_path
        else:
            alt_path = _project_root / "resources"
            return alt_path
    else:
        return get_project_root() / "resources"


def get_resource_path(*parts):
    resource_path = get_resources_path().joinpath(*parts)
    return resource_path


def is_frozen_env():
    return _is_frozen


def get_base_path():
    return get_project_root()


def get_src_path():
    root = get_project_root()
    if _is_frozen:
        src_path = root / "src" / "openchj_annotator"
        if src_path.exists():
            return src_path
        return root / "openchj_annotator"
    else:
        return root / "src" / "openchj-annotator"
