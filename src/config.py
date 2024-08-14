import tomli

default_config = {
    "main_window": {
        "confirm_action": ["save", "print"],
    },
    "create_distilling_tab_buttons": {
        "button_Save": False,
        "button_Print": False,
        "button_SavePrint": True,
    },
    "updater": {
        "allow_update": True,
    },
    "printer": {
        "copies": 2,
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


with open("config.toml", "rb") as conf_file:
    loaded_config = tomli.load(conf_file)
    config.update(loaded_config)
