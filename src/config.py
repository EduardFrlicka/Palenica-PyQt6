import tomli
import os

default_config = {
    "create_distilling_tab_buttons": {
        "button_Save": False,
        "button_Print": False,
        "button_SavePrint": True,
    },
    "updater": {
        "allow_update": True,
        "url": "https://api.github.com/repos/EduardFrlicka/Palenica-PyQt6/releases/latest",
    },
    "printer": {
        "copies": 2,
    },
    "database": {
        "engine": "",
        "user": "",
        "password": "",
        "host": "",
        "port": 0,
        "path": "",
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


config = Config()
config.update(default_config)

if os.path.exists("config.toml"):
    with open("config.toml", "rb") as conf_file:
        loaded_config = tomli.load(conf_file)
        config.update(loaded_config)
else:
    with open("config.toml", "w") as conf_file:
        for section_name, section in default_config.items():
            conf_file.write(f"[{section_name}]\n")
            for key, value in section.items():
                if value is True:
                    value = "true"
                elif value is False:
                    value = "false"
                elif isinstance(value, str):
                    value = f'"{value}"'
                elif value is None:
                    value = "null"

                conf_file.write(f"{key} = {value}\n")
            conf_file.write("\n")
