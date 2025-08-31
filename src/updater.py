from config import config
import requests
import json
import shutil
import zipfile
import subprocess
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import pyqtSignal

import messages
import threading

VERSION_FILE = "version.txt"


class UpdaterMsgBox(QMessageBox):
    update_downloaded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.update_downloaded.connect(self.close)

    def show(self):
        self.setText("Aktualizácia")
        self.setText(messages.UPDATE_IN_PROGRESS)
        self.setIcon(QMessageBox.Icon.Information)
        self.setStandardButtons(QMessageBox.StandardButton.NoButton)
        super().show()

    def exec(self):
        super().exec()

    def close(self):
        super().close()
        sys.exit()

if config.get("updater", "allow_updates", default=True):
    RELEASE_URL = config.get("updater", "url")
    latest_json = json.loads(requests.api.get(RELEASE_URL).text)
    zip_name = f"{latest_json['tag_name']}.zip"


def check_and_perform_update():
    if not config.get("updater", "allow_updates", default=True):
        return
    latest = get_latest()
    current = get_current()

    print(f"Latest version: {latest}, Current version: {current}")

    if latest > current:
        perform_update()
        pass

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)


def perform_update():
    msgBox = UpdaterMsgBox()

    def _download_and_run_updater():
        asset_url = find_asset_url("windows-latest.zip")
        download_file(asset_url, zip_name)

        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            if "updater.exe" in zip_ref.namelist():
                zip_ref.extract("updater.exe", ".")

        # if on windows, run the updater
        if sys.platform == "win32":
            subprocess.Popen(["start", ".\\updater.exe"], shell=True)
        else:
            print("Updater not supported on this platform")

        msgBox.update_downloaded.emit()

    msgBox.show()

    threading.Thread(target=_download_and_run_updater).start()

    print("Update in progress")

    msgBox.exec()


def extract_update(progress_callback, finished_callback):
    with zipfile.ZipFile(zip_name, "r") as zip_ref:
        filenames = zip_ref.namelist()
        for i, file in enumerate(filenames):
            if file == "updater.exe":
                continue
            zip_ref.extract(file, ".")
            progress_callback(i / len(filenames))

    save_current(latest_json["tag_name"])

    finished_callback()


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
    return latest_json["tag_name"]
