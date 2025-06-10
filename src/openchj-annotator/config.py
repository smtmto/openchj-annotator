import copy
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

try:
    from utils.path_manager import get_effective_config_file_path
except ImportError:

    def get_effective_config_file_path(filename="config.json") -> Path:
        return Path(".") / "config" / filename


class Config:
    DEFAULT_CONFIG = {
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

    def __init__(self, config_file_path_str: Optional[str] = None):
        import os
        from pathlib import Path

        is_frozen = os.environ.get("OPENCHJ_IS_FROZEN", "0") == "1"

        if is_frozen:
            if os.name == "nt":
                config_dir = (
                    Path(
                        os.environ.get(
                            "LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local")
                        )
                    )
                    / "OpenCHJAnnotator"
                )
            else:
                config_dir = Path(os.path.expanduser("~/.config")) / "OpenCHJAnnotator"

            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"

            if not self.config_path.exists():
                default_config = copy.deepcopy(self.DEFAULT_CONFIG)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
        else:
            # development mode
            if config_file_path_str is None:
                self.config_path = get_effective_config_file_path("config.json")
            else:
                self.config_path = Path(config_file_path_str)

        self.config = self._load_or_create_config()
        self._ensure_dynamic_defaults()

    def _load_or_create_config(self) -> Dict:
        if self.config_path.exists() and self.config_path.is_file():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config_data_from_file = json.load(f)
                merged_config = copy.deepcopy(self.DEFAULT_CONFIG)
                for key, value_from_file in config_data_from_file.items():
                    if (
                        key in merged_config
                        and isinstance(merged_config[key], dict)
                        and isinstance(value_from_file, dict)
                    ):
                        for sub_key, sub_value_from_file in value_from_file.items():
                            if sub_key in merged_config[key]:
                                merged_config[key][sub_key] = sub_value_from_file
                            else:
                                pass
                    elif key in merged_config:
                        merged_config[key] = value_from_file
                    else:
                        pass
                return merged_config
            except json.JSONDecodeError:
                logging.warning(
                    f"Failed to parse config file: {self.config_path}. "
                    "A new default config will be created and saved."
                )
            except Exception as e:
                logging.error(
                    f"Error loading config from {self.config_path}: {e}. "
                    "A new default config will be created and saved."
                )

        default_config = copy.deepcopy(self.DEFAULT_CONFIG)
        self._save_config_to_path(default_config, self.config_path)
        return default_config

    def _ensure_dynamic_defaults(self):
        if not self.config["output_settings"].get("default_directory"):
            try:
                from utils.file_utils import get_downloads_directory

                self.config["output_settings"][
                    "default_directory"
                ] = get_downloads_directory()
            except ImportError:
                logging.warning(
                    "utils.file_utils.get_downloads_directory could not be imported. Default output directory not set."
                )
                import os

                self.config["output_settings"]["default_directory"] = (
                    os.path.expanduser("~/Downloads")
                )
            except Exception as e:
                logging.warning(f"Error setting default_directory dynamically: {e}")
                import os

                self.config["output_settings"]["default_directory"] = (
                    os.path.expanduser("~/Downloads")
                )

    def _normalize_path_string(self, path_str: Optional[str]) -> Optional[str]:
        if path_str:
            return str(Path(path_str).as_posix())
        return None

    def _save_config_to_path(self, config_data: Dict, path_to_save: Path):
        try:
            path_to_save.parent.mkdir(parents=True, exist_ok=True)
            temp_path = path_to_save.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)

            temp_path.replace(path_to_save)

        except PermissionError as e:
            logging.error(f"Permission denied: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to save config to {path_to_save}: {e}")
            raise

    def save(self):
        try:
            self._save_config_to_path(self.config, self.config_path)

        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get_unidic_path(self, dict_type: str) -> Optional[str]:
        return self.config.get("unidic_paths", {}).get(dict_type)

    def set_unidic_path(self, dict_type: str, path: Optional[str]) -> None:
        if "unidic_paths" not in self.config:
            self.config["unidic_paths"] = {}
        self.config["unidic_paths"][dict_type] = path
        self.save()

    def get_active_dictionary(self) -> str:
        return self.config.get("active_dictionary", "lite")

    def set_active_dictionary(self, dict_type: str) -> None:
        if dict_type in self.config.get("unidic_paths", {}):
            self.config["active_dictionary"] = dict_type
        else:
            logging.warning(
                f"Attempted to set active dictionary to unknown type '{dict_type}'. Defaulting to 'lite'."
            )
            self.config["active_dictionary"] = "lite"
        self.save()

    def get_user_dictionary_path(self) -> Optional[str]:
        return self.config.get("user_dictionary_path")

    def set_user_dictionary_path(self, path: Optional[str]) -> None:
        self.config["user_dictionary_path"] = path
        self.save()

    def get_output_settings(self) -> Dict:
        return self.config.get(
            "output_settings", copy.deepcopy(self.DEFAULT_CONFIG["output_settings"])
        )

    def update_output_settings(self, settings: Dict) -> None:
        if "output_settings" not in self.config:
            self.config["output_settings"] = copy.deepcopy(
                self.DEFAULT_CONFIG["output_settings"]
            )

        for key, value in settings.items():
            if key in self.config["output_settings"]:
                self.config["output_settings"][key] = value
            else:
                logging.warning(
                    f"Ignoring unknown key '{key}' in update_output_settings."
                )
        self.save()

    def get_remove_tags_settings(self) -> Dict:
        return self.config.get(
            "remove_tags", copy.deepcopy(self.DEFAULT_CONFIG["remove_tags"])
        )

    def update_remove_tags_settings(self, settings: Dict) -> None:
        if "remove_tags" not in self.config:
            self.config["remove_tags"] = copy.deepcopy(
                self.DEFAULT_CONFIG["remove_tags"]
            )
        for key, value in settings.items():
            if key in self.config["remove_tags"]:
                self.config["remove_tags"][key] = value
        self.save()

    def get_regex_settings(self) -> Dict:
        return self.config.get(
            "regex_settings", copy.deepcopy(self.DEFAULT_CONFIG["regex_settings"])
        )

    def update_regex_settings(self, settings: Dict) -> None:
        if "regex_settings" not in self.config:
            self.config["regex_settings"] = copy.deepcopy(
                self.DEFAULT_CONFIG["regex_settings"]
            )
        for key, value in settings.items():
            if key in self.config["regex_settings"]:
                self.config["regex_settings"][key] = value
        self.save()

    def get_tag_special_settings(self) -> Dict:
        return self.config.get(
            "tag_special_settings",
            copy.deepcopy(self.DEFAULT_CONFIG["tag_special_settings"]),
        )

    def update_tag_special_settings(self, settings: Dict) -> None:
        if "tag_special_settings" not in self.config:
            self.config["tag_special_settings"] = copy.deepcopy(
                self.DEFAULT_CONFIG["tag_special_settings"]
            )
        for key, value in settings.items():
            if key in self.config["tag_special_settings"]:
                self.config["tag_special_settings"][key] = value
        self.save()

    def list_available_dictionaries(self) -> List[str]:
        unidic_paths = self.config.get("unidic_paths", {})
        return [
            dict_type for dict_type, path in unidic_paths.items() if path is not None
        ]
