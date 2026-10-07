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

try:
    from rich.highlighter import NullHighlighter
    from rich.logging import RichHandler
except ImportError:
    # Without rich the terminal log is plain text, so a run still starts and
    # can report which Python it uses
    RichHandler = None

# Every log line is also saved here, so you can read what a run did afterwards.
LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "test_run.log"


# Colour of the result word in a test's END line (used when rich is installed)
RESULT_STYLES = {
    "PASSED": "bold green",
    "FAILED": "bold red",
    "ERROR": "bold red",
    "SKIPPED": "bold yellow",
}

if RichHandler is not None:

    class ResultColourHandler(RichHandler):
        """A RichHandler that also colours PASSED, FAILED, ERROR and SKIPPED in a test's END line."""

        def render_message(self, record, message):
            """Return the message as styled text; only a test's END line gets coloured words."""
            text = super().render_message(record, message)
            if "========== END:" in message:
                for word, style in RESULT_STYLES.items():
                    text.highlight_words([word], style)
            return text


def _make_logger(name: str) -> logging.Logger:
    """
    Create a logger that writes to the terminal AND to logs/test_run.log,
    with a consistent "[LEVEL] message" format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        # Terminal output: coloured by level (INFO normal, WARNING yellow, ERROR red)
        # when rich is installed, plain "[LEVEL] message" lines when it is not.
        # markup=False so a text such as "[015] Microfinance" is printed as it is.
        if RichHandler is None:
            terminal_handler = logging.StreamHandler(sys.stdout)
            terminal_handler.setFormatter(logging.Formatter("[%(levelname)s] [%(name)s] %(message)s"))
        else:
            terminal_handler = ResultColourHandler(
                show_path=False,
                markup=False,
                rich_tracebacks=False,
                highlighter=NullHighlighter(),
                log_time_format="[%H:%M:%S]",
            )
            terminal_handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
        logger.addHandler(terminal_handler)

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
