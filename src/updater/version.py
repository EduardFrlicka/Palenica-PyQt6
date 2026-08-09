"""Comparing release tags.

GitHub hands out tags as strings and the previous implementation compared them
with a plain `>`, which orders "1.10.0" below "1.9.0" - updates would have
stopped working silently at the tenth patch release. Parse into a tuple.
"""

import re

from .log import log

# v1.2.3, 1.2.3, 1.2, 1.2.3-rc1, 1.2.3+build - anything else is not a version.
_TAG = re.compile(r"^v?(?P<release>\d+(?:\.\d+)*)(?:[-+](?P<pre>.+))?$")


def parse(tag: str) -> tuple | None:
    """Return a sortable key for `tag`, or None if it is not a version."""
    match = _TAG.match((tag or "").strip())
    if not match:
        return None

    release = tuple(int(part) for part in match.group("release").split("."))
    pre = match.group("pre")

    # A prerelease sorts below the release it leads up to: 1.2.0-rc1 < 1.2.0.
    # Prereleases themselves compare as text, so rc10 lands before rc2 - fine
    # while releases stay plain, and never worse than not comparing at all.
    return (release, 0, pre) if pre else (release, 1, "")


def is_newer(latest: str, current: str) -> bool:
    """True if `latest` supersedes `current`."""
    left, right = parse(latest), parse(current)

    if left is None or right is None:
        if not (current or "").strip():
            # No version.txt - an install predating the marker, or one whose
            # last update failed part way. Update and let it self-heal.
            log.info("No current version recorded, treating %s as newer", latest)
            return True

        # The tag naming drifted away from vN.N.N. Fall back to a text compare
        # rather than refusing to ever update again, but say so.
        log.warning("Cannot parse versions (latest=%r current=%r), comparing as text", latest, current)
        return (latest or "").strip() > current.strip()

    return _padded(left, right) > _padded(right, left)


def _padded(key: tuple, other: tuple) -> tuple:
    """Zero-extend the release part so 1.2 and 1.2.0 compare equal."""
    release = key[0]
    width = max(len(release), len(other[0]))
    return (release + (0,) * (width - len(release)),) + key[1:]
