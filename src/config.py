import json
import tomllib as tomli

import paths

default_config = {
    "database": {
        # Turso. Take the database URL from the dashboard, swap the libsql://
        # scheme for sqlite+turso:// and append the auth token as
        # ?authToken=<token>. A local file works with the same driver:
        # "sqlite+turso:///palenica.db"
        "url": "",
    },
    "create_distilling_tab_buttons": {
        "button_Save": False,
        "button_Print": False,
        "button_SavePrint": True,
    },
    "updater": {
        "allow_updates": True,
        "url": "https://api.github.com/repos/EduardFrlicka/Palenica-PyQt6/releases/latest",
        # Seconds to wait on GitHub. A slow network delays startup by at most
        # this much; the check is skipped on any failure.
        "timeout": 10,
        # Release asset to download, overriding the name derived from the
        # platform. Mainly a testing hook - it lets a machine with no published
        # build of its own exercise the whole update path.
        "asset": "",
        # Updating a source checkout would unpack a packaged build over it, so
        # it is refused unless this is switched on deliberately.
        "allow_source_updates": False,
    },
    "printer": {
        "copies": 2,
    },
    "main_window": {
        "tabs": ["create_distilling"],
    },
}


class Config:
    def __init__(self):
        self.config = {}

    def update(self, new_config: dict):
        for key, value in new_config.items():
            key_dict = self.config.get(key)
            if isinstance(value, dict) and isinstance(key_dict, dict):
                key_dict.update(value)
            else:
                self.config[key] = value

    def get(self, *keys, default=None):
        current = self.config
        for key in keys:
            if key not in current:
                return default

            current = current.get(key)
        return current


def _toml_value(value) -> str:
    """Serialise a default so the file we write can be read back.

    The previous version stringified anything that was not a bool or a str with
    an f-string, which turned the tabs list into Python's ['create_distilling']
    - single quotes, which TOML rejects. The generated config then failed to
    parse on the very next start.
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    # JSON's string and array syntax is a subset of TOML's.
    return json.dumps(value, ensure_ascii=False)


def _write_default(path) -> None:
    with open(path, "w", encoding="utf-8") as conf_file:
        for section_name, section in default_config.items():
            conf_file.write(f"[{section_name}]\n")
            for key, value in section.items():
                conf_file.write(f"{key} = {_toml_value(value)}\n")
            conf_file.write("\n")


config = Config()
config.update(default_config)

# Anchored to the installation, not the working directory: a shortcut with a
# "Start in" field used to send the app looking for a config that was not there
# and then write a fresh one somewhere the user would never find it.
config_path = paths.config_file()

if config_path.exists():
    with open(config_path, "rb") as conf_file:
        config.update(tomli.load(conf_file))
else:
    _write_default(config_path)
