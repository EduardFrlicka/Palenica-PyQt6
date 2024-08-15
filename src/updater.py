from config import config
import requests
import json
import shutil
import zipfile
import subprocess
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
import messages
import threading

VERSION_FILE = "version.txt"


if config.get("updater", "allow_updates", default=True):
    RELEASE_URL = config.get("updater", "url")
    latest_json = json.loads(requests.api.get(RELEASE_URL).text)
    zip_name = f"{latest_json['tag_name']}.zip"


def update():
    if not config.get("updater", "allow_updates", default=True):
        return
    latest = get_latest()
    current = get_current()
    if latest > current:
        _update()


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)


def _update():
    def update_dialog_thread():
        msgBox.setText("Aktualizácia")
        msgBox.setText(messages.UPDATE_IN_PROGRESS)
        msgBox.setIcon(QMessageBox.Icon.Information)
        msgBox.setStandardButtons()
        msgBox.show()
        msgBox.exec()

    msgBox = QMessageBox()
    # run msgBox in separate thread
    threading.Thread(target=update_dialog_thread).start()

    asset_url = find_asset_url("windows-latest.zip")
    download_file(asset_url, zip_name)

    with zipfile.ZipFile(zip_name, "r") as zip_ref:
        if "updater.exe" in zip_ref.namelist():
            zip_ref.extract("updater.exe", ".")

    subprocess.run(["updater.exe"], shell=True)
    msgBox.close()
    exit()


def find_asset_url(asset_name):
    for asset in latest_json["assets"]:
        if asset["name"] == asset_name:
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


def main():
    app = QApplication(sys.argv)

    

    def dialog_thread():

    


if __name__ == "__main__":
    main()
