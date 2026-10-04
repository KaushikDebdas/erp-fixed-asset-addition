"""
Three loggers, per skills/logging-reporting.md:
- action_logger: did the Playwright action itself succeed?
- assertion_logger: did the expected business outcome actually happen?
- test_logger: marks where each test starts and ends (written by conftest.py).
Keep action and assertion logs separate — a successful click is not a passed business test.
"""
import logging
import sys
from pathlib import Path

# Every log line is also saved here, so you can read what a run did afterwards.
LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "test_run.log"


def _make_logger(name: str) -> logging.Logger:
    """
    Create a logger that writes to the terminal AND to logs/test_run.log,
    with a consistent "[LEVEL] message" format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        # Terminal output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(stream_handler)

        # File output (the logs/ folder is created if it does not exist yet)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)
    return logger


action_logger = _make_logger("action")
assertion_logger = _make_logger("assertion")
test_logger = _make_logger("test")
