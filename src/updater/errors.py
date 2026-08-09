"""Failures the updater raises.

Every message is user-facing Slovak: these reach a dialog in the updater binary,
where there is no console and no traceback to fall back on.
"""


class UpdateError(Exception):
    """An update could not be completed. The install is left as it was."""


class UpdateCancelled(UpdateError):
    """The user cancelled the download."""
