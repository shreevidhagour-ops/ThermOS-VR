"""Overwrite protection and environment metadata shared by the runner scripts."""

import argparse
import os
import platform
import sys
from importlib import metadata


def parse_overwrite_flag(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--overwrite", action="store_true",
        help="allow replacing files in an existing output directory",
    )
    return parser.parse_args().overwrite


def ensure_writable(directory, overwrite):
    """
    Refuse to write into a directory that already holds files (other than
    the Google Drive desktop.ini) unless --overwrite was given. Exits with
    status 2 before any simulation or file write happens.
    """
    existing = []
    if os.path.isdir(directory):
        existing = [f for f in os.listdir(directory) if f.lower() != "desktop.ini"]

    if existing and not overwrite:
        print(
            f"REFUSING TO WRITE: {directory} already contains "
            f"{len(existing)} file(s). Nothing was changed.\n"
            f"Re-run with --overwrite to replace them.",
            file=sys.stderr,
        )
        sys.exit(2)

    os.makedirs(directory, exist_ok=True)


def environment_versions():
    versions = {
        "python": sys.version,
        "platform": platform.platform(),
    }
    for package in ("pandas", "matplotlib", "numpy"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "not installed"
    return versions
