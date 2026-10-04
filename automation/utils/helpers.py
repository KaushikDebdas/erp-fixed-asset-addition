"""
helpers.py: small helper functions that any test or page object can use.

Why one file: so a new team member has ONE place to look. Before writing a new
helper, check here first. Add new helpers under the matching section below,
or create a new section if the topic is new.

How to use:
    from utils.helpers import unique_name, days_from_today

Sections:
    1. Test data that must be different every run (names, numbers, text)
    2. Dates (today, N days from today)
    3. Calendar widgets (pick a month and year in the month picker)
"""
import random
import string
from datetime import datetime, timedelta

from playwright.sync_api import Locator, Page


# ---------------------------------------------------------------------------
# 1. Test data that must be different every run
# Why: many screens reject duplicate names or reference numbers. If a test
# types the same "Test Voucher" twice, the second run fails for the wrong reason.
# ---------------------------------------------------------------------------

def unique_name(prefix: str) -> str:
    """
    Return the prefix plus the current date and time.

    Example: unique_name("Voucher") -> "Voucher_20261001_143015"
    """
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def random_number(digits: int = 6) -> str:
    """
    Return a string of random digits.

    Example: random_number(4) -> "5821"
    """
    return "".join(random.choice(string.digits) for _ in range(digits))


def random_text(length: int = 8) -> str:
    """
    Return random capital letters. Handy for free-text fields.

    Example: random_text(5) -> "QWKTZ"
    """
    return "".join(random.choice(string.ascii_uppercase) for _ in range(length))


# ---------------------------------------------------------------------------
# 2. Dates
# Why: tests must never hardcode a date like "2026-10-01" because it will be
# wrong tomorrow. These build dates relative to today.
# ---------------------------------------------------------------------------

# Date format used when typing into a date field. Change this ONE line if the
# application expects another format (e.g. "%Y-%m-%d").
DEFAULT_DATE_FORMAT = "%d/%m/%Y"


def today(date_format: str = DEFAULT_DATE_FORMAT) -> str:
    """
    Return today's date as text.

    Example: today() -> "01/10/2026"
    """
    return datetime.now().strftime(date_format)


def days_from_today(days: int, date_format: str = DEFAULT_DATE_FORMAT) -> str:
    """
    Return the date N days from today. Use a negative number for the past.

    Example: days_from_today(7) -> "08/10/2026"
             days_from_today(-1) -> "30/09/2026"
    """
    target = datetime.now() + timedelta(days=days)
    return target.strftime(date_format)


def day_of_month(date_text: str, date_format: str = DEFAULT_DATE_FORMAT) -> str:
    """
    Return just the day-of-month number (no leading zero) from a date string.

    Used to match a date already shown on screen (e.g. a read-only
    "Registration Date" field) to the day cell of a calendar pop-up that is
    already showing the same month and year.

    Example: day_of_month("20/09/2026") -> "20"
             day_of_month("03/09/2026") -> "3"
    """
    parsed = datetime.strptime(date_text, date_format)
    return str(parsed.day)


# ---------------------------------------------------------------------------
# 3. Calendar widgets
# Calendar pickers differ on every screen. Only add a helper here after the
# real calendar has been explored, so it matches the actual page.
# ---------------------------------------------------------------------------

def pick_month_year(page: Page, date_field: Locator, year: int, month: int) -> None:
    """
    Choose a month and year in the Finance app's month picker.

    The picker shows a year at the top with a back arrow (<) and a forward
    arrow (>), and a grid of 12 months (Jan ... Dec).

    Example: pick_month_year(page, from_date_field, 2025, 7)  -> "07-2025"
    """
    # Step 1: click the date box so the month picker opens
    date_field.click()

    # The picker that is open right now (there can be more than one on the page,
    # so we only look at the visible one)
    picker = page.locator(".datepicker-months:visible")

    # Step 2: read the year the picker is showing, e.g. "2026"
    shown_year = int(picker.locator(".datepicker-switch").inner_text())

    # Step 3: click the back or forward arrow until the wanted year is showing
    arrow = picker.locator(".prev") if year < shown_year else picker.locator(".next")
    for _ in range(abs(year - shown_year)):
        arrow.click()

    # Step 4: click the wanted month. The 12 months are in order, so month 1
    # is the first item and month 12 is the last.
    picker.locator("span.month").nth(month - 1).click()
