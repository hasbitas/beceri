"""Major-version dependency resolution and lock file generation."""

from .lockfile import generate_lock, parse_lock, render_lock
from .solver import ConflictError, ResolutionError, resolve
from .versions import format_version, newest, parse_version

__all__ = [
    "ConflictError", "ResolutionError", "format_version", "generate_lock", "newest",
    "parse_lock", "parse_version", "render_lock", "resolve",
]
