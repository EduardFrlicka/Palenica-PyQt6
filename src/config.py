import tomli

with open("config.toml", "rb") as conf_file:
    config = tomli.load(conf_file)
