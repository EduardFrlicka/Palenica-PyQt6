"""GitHub Releases client and per-platform asset selection."""

from dataclasses import dataclass
import platform
import sys

import requests

from .errors import UpdateError
from .log import log

USER_AGENT = "Palenica-Updater"

# The unauthenticated API allows 60 requests an hour per address. The app spends
# one per launch, which is ample unless a site NATs many installs together - in
# which case the 403 below is reported and the app starts as normal.
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": USER_AGENT,
}

DEFAULT_TIMEOUT = 10

# platform.machine() spells the same architecture differently per OS.
_ARCH = {
    "amd64": "x86_64",
    "x86_64": "x86_64",
    "arm64": "arm64",
    "aarch64": "arm64",
}


@dataclass(frozen=True)
class Release:
    tag: str
    assets: dict[str, str]

    @classmethod
    def fetch(cls, url: str, timeout: float = DEFAULT_TIMEOUT) -> "Release":
        response = requests.get(url, headers=HEADERS, timeout=timeout)

        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise UpdateError("GitHub API rate limit reached")

        response.raise_for_status()
        payload = response.json()

        tag = payload.get("tag_name")
        if not tag:
            raise UpdateError(f"Release at {url} has no tag_name")

        assets = {
            asset["name"]: asset["browser_download_url"]
            for asset in payload.get("assets", [])
            if asset.get("name") and asset.get("browser_download_url")
        }
        return cls(tag=tag, assets=assets)

    def find_asset(self, names: list[str]) -> str | None:
        """URL of the first asset in `names` this release actually carries."""
        for name in names:
            if name in self.assets:
                return self.assets[name]

        log.info(
            "Release %s carries no asset matching %s (has: %s)",
            self.tag,
            names,
            sorted(self.assets) or "none",
        )
        return None


def asset_names() -> list[str]:
    """Release assets that would run on this machine, best match first.

    An empty list means there is no build for this platform - the caller logs it
    and moves on, which is how Linux and macOS degrade gracefully while Windows
    stays the real target.
    """
    arch = _ARCH.get(platform.machine().lower(), platform.machine().lower())

    if sys.platform == "win32":
        # windows-latest.zip is what the pre-rewrite updater looked for and what
        # CI still publishes alongside the new name; keep accepting it so an
        # install that sits out a release can still find something.
        return [f"palenica-windows-{arch}.zip", "windows-latest.zip"]
    if sys.platform == "linux":
        return [f"palenica-linux-{arch}.zip"]
    if sys.platform == "darwin":
        return [f"palenica-macos-{arch}.zip"]
    return []
