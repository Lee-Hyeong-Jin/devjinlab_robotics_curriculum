"""Robotics curriculum and learning-assist platform."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _installed_version

try:
    # One source of truth: pyproject.toml, read back from the installed distribution.
    # A release only has to bump the version there (docs/operations/RELEASE.md).
    __version__ = _installed_version("robotics-curriculum")
except PackageNotFoundError:  # imported from a source tree that was never installed
    __version__ = "0+unknown"

__all__ = ["__version__"]
