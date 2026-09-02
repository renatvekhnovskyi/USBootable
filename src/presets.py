import json
from pathlib import Path


PRESETS_FILE = Path(__file__).parent / "presets.json"
CONFIG_FILE = Path(__file__).parent / "config.json"


def _load_presets() -> dict:
    with PRESETS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {
            "preset": "os_boot"
        }

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_config(config: dict) -> None:
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            config,
            file,
            indent=2
        )


def list_presets() -> list[str]:
    """
    Return all available preset names.
    """

    data = _load_presets()

    return list(data["presets"].keys())


def get_current_preset() -> str:
    """
    Return the currently selected preset.
    """

    config = _load_config()

    return config["preset"]


def get_preset(name: str) -> dict:
    """
    Return a complete preset definition.
    """

    data = _load_presets()

    try:
        return data["presets"][name]
    except KeyError:
        available = ", ".join(data["presets"].keys())

        raise ValueError(
            f"Unknown preset '{name}'. "
            f"Available presets: {available}"
        )


def set_preset(name: str) -> None:
    """
    Set the active benchmark preset.
    """

    # Validate before modifying the config.
    get_preset(name)

    config = _load_config()
    config["preset"] = name

    _save_config(config)
