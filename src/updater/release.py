"""GitHub Releases client and per-platform asset selection."""

from dataclasses import dataclass
import platform
import sys
from urllib.parse import urlparse

import requests

from . import version
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

API_ROOT = "https://api.github.com"

# One page is plenty: the newest releases come first, and only the newest
# stable and the newest beta matter.
RELEASES_PER_PAGE = 50

# platform.machine() spells the same architecture differently per OS.
_ARCH = {
    "amd64": "x86_64",
    "x86_64": "x86_64",
    "arm64": "arm64",
    "aarch64": "arm64",
}


@dataclass(frozen=True)
class Repository:
    """The GitHub repository releases come from.

    The config holds a URL so that it can be pasted from a browser, but which
    endpoint gets called is decided here. Any URL that names the repository
    works, which keeps configs written for the old /releases/latest endpoint
    valid:

        https://github.com/<owner>/<repo>
        https://api.github.com/repos/<owner>/<repo>/releases/latest
    """

    owner: str
    name: str

    @classmethod
    def from_url(cls, url: str) -> "Repository":
        parsed = urlparse((url or "").strip())
        host = parsed.netloc.lower()
        segments = [segment for segment in parsed.path.split("/") if segment]

        if host == "api.github.com" and segments[:1] == ["repos"]:
            segments = segments[1:]
        elif host not in ("github.com", "www.github.com"):
            raise UpdateError(f"Not a GitHub repository URL: {url!r}")

        if len(segments) < 2:
            raise UpdateError(f"No owner/repository in {url!r}")

        return cls(owner=segments[0], name=segments[1].removesuffix(".git"))

    @property
    def releases_url(self) -> str:
        return f"{API_ROOT}/repos/{self.owner}/{self.name}/releases"


@dataclass(frozen=True)
class Release:
    tag: str
    assets: dict[str, str]
    prerelease: bool = False

    @classmethod
    def from_payload(cls, payload: dict) -> "Release":
        tag = payload.get("tag_name")
        if not tag:
            raise UpdateError("Release has no tag_name")

        assets = {
            asset["name"]: asset["browser_download_url"]
            for asset in payload.get("assets", [])
            if asset.get("name") and asset.get("browser_download_url")
        }
        # Trust either signal: the flag set on GitHub, or a tag that reads as a
        # beta. A release missing one of them must still not reach stable users.
        prerelease = bool(payload.get("prerelease")) or version.is_prerelease(tag)
        return cls(tag=tag, assets=assets, prerelease=prerelease)

    @classmethod
    def fetch_all(cls, repository: Repository, timeout: float = DEFAULT_TIMEOUT) -> list["Release"]:
        """Published releases, betas included. Drafts are left out."""
        response = requests.get(
            repository.releases_url,
            params={"per_page": RELEASES_PER_PAGE},
            headers=HEADERS,
            timeout=timeout,
        )

        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise UpdateError("GitHub API rate limit reached")

        response.raise_for_status()

        releases = []
        for payload in response.json():
            if payload.get("draft") or not payload.get("tag_name"):
                continue
            releases.append(cls.from_payload(payload))
        return releases

    def has_asset(self, names: list[str]) -> bool:
        return any(name in self.assets for name in names)

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


def pick(releases: list[Release], current: str, allow_beta: bool, names: list[str]) -> Release | None:
    """The release to install, or None to stay where we are.

    With allow_beta the highest version wins, beta or not. Without it only
    stable releases count - and if a beta is installed, the newest stable one
    is installed even though its number is lower. That is how switching betas
    off returns to the stable line.

    Releases without a build for this platform are skipped, so a release whose
    assets are still uploading does not hide the one before it.
    """
    candidates = [r for r in releases if (allow_beta or not r.prerelease) and r.has_asset(names)]
    if not candidates:
        log.info("No %srelease carries any of %s", "" if allow_beta else "stable ", names)
        return None

    best = max(candidates, key=lambda r: _sort_key(r.tag))

    if version.is_newer(best.tag, current):
        return best

    if not allow_beta and version.is_prerelease(current):
        log.info("Betas are switched off, returning from %s to %s", current, best.tag)
        return best

    return None


def _sort_key(tag: str) -> tuple:
    # Unparseable tags sort first, so they are never preferred over a real one.
    key = version.parse(tag)
    return (1, key) if key is not None else (0, ())


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
