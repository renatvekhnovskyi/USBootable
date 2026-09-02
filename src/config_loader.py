from json import dump, load
from paths import get_app_path


def load_config():
    config_path = get_app_path() / "config" / "std.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return load(f)


def load_preset():
    preset_path = get_app_path() / "config" / "preset.json"

    if not preset_path.exists():
        return "os_boot"

    with open(preset_path, "r", encoding="utf-8") as f:
        return load(f)["preset"]


def save_preset(preset: str):
    preset_path = get_app_path() / "config" / "preset.json"

    with open(preset_path, "w", encoding="utf-8") as f:
        dump({"preset": preset}, f, indent=2)
