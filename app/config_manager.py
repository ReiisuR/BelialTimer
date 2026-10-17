import json
import os
import tempfile
from copy import deepcopy

from PySide6.QtCore import QStandardPaths

from .profile_manager import (
    DEFAULT_PROFILE,
    validate_profile
)


DEFAULT_CONFIG = {
    "sound_enabled": True,
    "visual_alerts_enabled": True,
    "compact_mode": False,
    "test_mode": False,
    "background_opacity": 85,
    "text_opacity": 85,
    "opacities_linked": True,
    "header_art": "sentada",
    "window_positions": {
        "normal": None,
        "compact": None
    },
    "custom_profile": DEFAULT_PROFILE
}


def get_config_path():

    config_directory = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )

    return os.path.join(
        config_directory,
        "config.json"
    )


def load_config(path=None):

    config_path = path or get_config_path()
    config = deepcopy(DEFAULT_CONFIG)

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            stored_config = json.load(config_file)
    except FileNotFoundError:
        return config, None
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return config, (
            "Não foi possível ler as configurações salvas. "
            "Os valores padrão serão usados.\n\n{}".format(error)
        )

    if not isinstance(stored_config, dict):
        return config, (
            "O arquivo de configurações não contém um objeto JSON. "
            "Os valores padrão serão usados."
        )

    invalid_keys = []

    for key in (
        "sound_enabled",
        "visual_alerts_enabled",
        "compact_mode",
        "test_mode"
    ):
        if key not in stored_config:
            continue

        if type(stored_config[key]) is bool:
            config[key] = stored_config[key]
        else:
            invalid_keys.append(key)

    legacy_opacity = stored_config.get("window_opacity")
    has_new_opacity = (
        "background_opacity" in stored_config
        or "text_opacity" in stored_config
    )

    if (
        "window_opacity" in stored_config
        and not has_new_opacity
    ):
        if type(legacy_opacity) is int and 0 <= legacy_opacity <= 100:
            config["background_opacity"] = legacy_opacity
            config["text_opacity"] = 100
            config["opacities_linked"] = False
        else:
            invalid_keys.append("window_opacity")

    for key in ("background_opacity", "text_opacity"):
        if key not in stored_config:
            continue

        opacity = stored_config[key]
        if type(opacity) is int and 0 <= opacity <= 100:
            config[key] = opacity
        else:
            invalid_keys.append(key)

    if "opacities_linked" in stored_config:
        if type(stored_config["opacities_linked"]) is bool:
            config["opacities_linked"] = stored_config["opacities_linked"]
        else:
            invalid_keys.append("opacities_linked")

    if "header_art" in stored_config:
        if stored_config["header_art"] in ("sentada", "deitada"):
            config["header_art"] = stored_config["header_art"]
        else:
            invalid_keys.append("header_art")

    if "window_positions" in stored_config:
        stored_positions = stored_config["window_positions"]
        if isinstance(stored_positions, dict):
            for mode in ("normal", "compact"):
                if mode not in stored_positions:
                    continue

                position = stored_positions[mode]
                if position is None:
                    config["window_positions"][mode] = None
                elif (
                    isinstance(position, list)
                    and len(position) == 2
                    and all(type(coordinate) is int for coordinate in position)
                    and all(-100000 <= coordinate <= 100000 for coordinate in position)
                ):
                    config["window_positions"][mode] = position
                else:
                    invalid_keys.append("window_positions.{}".format(mode))
        else:
            invalid_keys.append("window_positions")

    if config["opacities_linked"]:
        config["text_opacity"] = config["background_opacity"]

    if "custom_profile" in stored_config:
        profile, profile_error = validate_profile(
            stored_config["custom_profile"]
        )

        if profile_error:
            invalid_keys.append("custom_profile")
        else:
            config["custom_profile"] = profile

    if invalid_keys:
        return config, (
            "Algumas configurações têm valores inválidos e foram "
            "substituídas pelos padrões: {}.".format(
                ", ".join(invalid_keys)
            )
        )

    return config, None


def save_config(config, path=None):

    config_path = path or get_config_path()
    config_directory = os.path.dirname(
        os.path.abspath(config_path)
    )
    os.makedirs(config_directory, exist_ok=True)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=config_directory,
            prefix=".config-",
            suffix=".tmp",
            delete=False
        ) as config_file:
            temporary_path = config_file.name
            json.dump(
                config,
                config_file,
                ensure_ascii=False,
                indent=2
            )
            config_file.write("\n")

        os.replace(temporary_path, config_path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
