import logging
import os
from pathlib import Path


def setup_logger():
    """
    Configure global logging for the project.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )


def get_project_root():
    """
    Returns the root directory of the project.
    """
    return Path(__file__).resolve().parents[1]


def ensure_directory(path):
    """
    Creates a directory if it does not exist.
    """
    os.makedirs(path, exist_ok=True)