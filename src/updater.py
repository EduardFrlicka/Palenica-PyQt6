from config import config
import requests
import json
import shutil
import zipfile
import os

RELEASE_URL = config["updater"].get("url")
VERSION_FILE = "version.txt"

latest_json = json.loads(requests.api.get(RELEASE_URL).text)

def update():
    if not config.get("update", True):
        return
    latest = get_latest()
    current = get_current()
    if latest > current:
        _update()


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def _update():
    local_name = f"{latest_json['tag_name']}.zip"
    asset_url = find_asset_url("windows-latest.zip")
    download_file(asset_url, local_name)
    with zipfile.ZipFile(local_name, 'r') as zip_ref:
        zip_ref.extractall("..")
    save_current(get_latest())


def find_asset_url(asset_name):
    for asset in latest_json["assets"]:
        if asset["name"] == asset_name:
            print(asset["browser_download_url"])
            return asset["browser_download_url"]


def save_current(version):
    with open(VERSION_FILE, "w") as f:
        f.write(version)


def get_current():
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    except OSError:
        return ""


def get_latest():
    return latest_json["published_at"]
