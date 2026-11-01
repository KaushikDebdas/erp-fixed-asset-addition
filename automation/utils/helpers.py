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
import re
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


def employee_pin_from_username(username: str, length: int = 8) -> str:
    """
    Return the employee PIN of a user whose login name is the PIN without its
    leading zeros. Returns "" when the login name is not all digits.

    Example: employee_pin_from_username("15370") -> "00015370"
    """
    if not username or not username.isdigit():
        return ""
    return username.zfill(length)


def simplify_office_text(text: str) -> str:
    """
    Return the text in lower case without spaces, hyphens and the leading zeros of
    an office code, so two spellings of one office compare equal.

    Example: "[BO - 0272] Kendua" and "[BO-272]Kendua" both give "[bo272]kendua"
    """
    text = text.lower().replace(" ", "").replace("-", "")
    return re.sub(r"(?<=\D)0+(?=\d)", "", text)


def bracket_code_of(text: str) -> str:
    """
    Return the text inside the first square brackets, or the whole text when there are none.

    Example: bracket_code_of("Head Office [ BDHO ]") -> "BDHO"
    """
    found = re.search(r"\[\s*([^\]]+?)\s*\]", text)
    if found:
        return found.group(1)
    return text.strip()


def expected_columns(wanted: list, found: list, optional: list) -> list:
    """
    Return the wanted column headings, leaving out an optional heading that the screen does not show.
    Some columns (for example Department) only appear for offices that have them.

    Example: expected_columns(["SL", "Department"], ["SL"], ["Department"]) -> ["SL"]
    """
    columns = []
    for heading in wanted:
        if heading in optional and heading not in found:
            continue
        columns.append(heading)
    return columns


def search_word_of(text: str) -> str:
    """
    Return the longest run of letters and digits in the text. It is a good word to type in a
    search box, because the search finds every entry that contains it.

    Example: search_word_of("[BO-0233]-Chagalnaiya") -> "Chagalnaiya"
    """
    words = re.findall(r"[A-Za-z0-9]+", text)
    if not words:
        return text
    return max(words, key=len)


def challan_row_problems(row: dict, challan_data: dict, sending_branch: str, status_column: str, in_number_column: str) -> list:
    """
    Compare the In-Challan grid row of an approved challan with the challan data it was created
    with. Returns one sentence per difference (an empty list when everything matches): status
    APPROVED, an In Challan number, From and To Project, Sending Branch and Receiving Branch
    (spaces, hyphens and leading zeros are ignored). `row` is {column heading: cell text}.
    """
    problems = []
    if row.get(status_column) != "APPROVED":
        problems.append(f"{status_column}: expected 'APPROVED' but found '{row.get(status_column)}'")
    if row.get(in_number_column, "") == "":
        problems.append(f"{in_number_column}: expected a number but the cell is empty")
    for column, key in [("From Project", "from_project"), ("To Project", "to_project")]:
        if row.get(column) != challan_data[key]:
            problems.append(f"{column}: expected '{challan_data[key]}' but found '{row.get(column)}'")
    if not office_matches(row.get("Sending Branch", ""), sending_branch):
        problems.append(f"Sending Branch: expected one containing '{sending_branch}' but found '{row.get('Sending Branch')}'")
    wanted_receiving = simplify_office_text(challan_data["receiving_branch"])
    if wanted_receiving not in simplify_office_text(row.get("Receiving Branch", "")):
        problems.append(
            f"Receiving Branch: expected one containing '{challan_data['receiving_branch']}' but found '{row.get('Receiving Branch')}'"
        )
    return problems


def office_words(text: str) -> set:
    """
    Return the words and numbers of an office text in lower case, with the leading zeros of a
    number removed. The order and the brackets do not matter, so the two ways the ERP writes
    one office give the same words.

    Example: office_words("Chagalnaiya [ 0233 ]") -> {"chagalnaiya", "233"}
             office_words("[BO - 0233] Chagalnaiya") -> {"bo", "233", "chagalnaiya"}
    """
    words = re.findall(r"[A-Za-z]+|\d+", text)
    return {word.lower().lstrip("0") or "0" for word in words}


def office_matches(shown: str, wanted: str) -> bool:
    """
    Return True when one of the two texts has all the words of the other, whatever the order,
    brackets, spaces, hyphens or leading zeros (one spelling may leave out the office type, such
    as BO). Use it to check that a screen shows the office a user chose. When `wanted` is empty
    (no DEFAULT_BRANCH in .env: the user has one office), any office that is shown is accepted.

    Example: office_matches("[BO - 0233] Chagalnaiya", "Chagalnaiya [ 0233 ]") -> True
    """
    if not wanted:
        return shown.strip() != ""
    shown_words = office_words(shown)
    wanted_words = office_words(wanted)
    return wanted_words <= shown_words or shown_words <= wanted_words


def find_one_text(names: list, wanted: str, what: str) -> str:
    """
    Return the one name that matches `wanted` (an exact match wins over a partial one; the order
    of the words, brackets, spaces, hyphens and leading zeros are ignored). Stops with a message
    listing the names when none or several match. `what` names the kind of entry in the message,
    e.g. "Receiving Branch".
    """
    exact = [name for name in names if office_words(name) == office_words(wanted)]
    partial = [name for name in names if office_words(wanted) <= office_words(name)]
    matches = exact or partial
    assert len(matches) == 1, f"{what} '{wanted}' matched {len(matches)} entries, expected 1. Entries: {names}"
    return matches[0]


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
