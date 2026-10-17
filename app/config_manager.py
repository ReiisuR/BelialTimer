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
