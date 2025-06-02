from typing import List, Optional, TypedDict

from config import Config


class TagSettings(TypedDict, total=False):
    enabled: bool
    types: List[str]
    mode: str


class RegexPatternItem(TypedDict, total=False):
    pattern: str
    replacement: str
    enabled: bool


class RegexSettings(TypedDict, total=False):
    enabled: bool
    patterns: List[RegexPatternItem]


class WhitespaceSettings(TypedDict, total=False):
    remove_half_space: bool
    remove_full_space: bool
    remove_newline: bool


class TagPatternItem(TypedDict, total=False):
    bracket_type: str
    tag_content: str
    surface_form: str
    pos_value: str


class TagSpecialSettings(TypedDict, total=False):
    tag_patterns: List[TagPatternItem]


class FormatSettings(TypedDict, total=False):
    tag_settings: TagSettings
    regex_settings: RegexSettings
    whitespace_settings: WhitespaceSettings
    aozora_cleanup: bool
    tag_special_settings: TagSpecialSettings


class SettingsModel:
    def __init__(self, config: Optional[Config] = None):
        self.config = config

    def load_settings(self) -> FormatSettings:
        if not self.config:
            return self._get_default_settings()

        config_dict = self.config.config
        tag_settings = config_dict.get("remove_tags", {})
        regex_settings = config_dict.get("regex_settings", {})
        output_settings = config_dict.get("output_settings", {})
        whitespace_settings = {
            "remove_half_space": output_settings.get("remove_half_space", False),
            "remove_full_space": output_settings.get("remove_full_space", False),
            "remove_newline": output_settings.get("remove_newline", False),
        }

        aozora_cleanup = config_dict.get("aozora_cleanup", False)
        tag_special_settings = config_dict.get(
            "tag_special_settings", {"tag_patterns": []}
        )

        return {
            "tag_settings": tag_settings,
            "regex_settings": regex_settings,
            "whitespace_settings": whitespace_settings,
            "aozora_cleanup": aozora_cleanup,
            "tag_special_settings": tag_special_settings,
        }

    def save_settings(self, settings: FormatSettings) -> None:
        if not self.config:
            return

        config_dict = self.config.config

        if "tag_settings" in settings:
            config_dict["remove_tags"] = settings["tag_settings"]

        if "regex_settings" in settings:
            config_dict["regex_settings"] = settings["regex_settings"]

        if "whitespace_settings" in settings:
            if "output_settings" not in config_dict:
                config_dict["output_settings"] = {}
            config_dict["output_settings"].update(settings["whitespace_settings"])

        if "aozora_cleanup" in settings:
            config_dict["aozora_cleanup"] = settings["aozora_cleanup"]

        if "tag_special_settings" in settings:
            config_dict["tag_special_settings"] = settings["tag_special_settings"]

        self.config.save()

    def _get_default_settings(self) -> FormatSettings:
        return {
            "tag_settings": {
                "enabled": False,
                "types": [],
                "mode": "remove_with_content",
            },
            "regex_settings": {"enabled": False, "patterns": []},
            "whitespace_settings": {
                "remove_half_space": False,
                "remove_full_space": False,
                "remove_newline": False,
            },
            "aozora_cleanup": False,
            "tag_special_settings": {"tag_patterns": []},
        }

    def clear_settings(self) -> None:
        if not self.config:
            return

        default_settings = self._get_default_settings()
        self.save_settings(default_settings)
