"""
Computes and creates the folder for the current test run, once per pytest
session. Every artifact from one execution — screenshots, traces, Allure
results, the generated HTML report — lives together under:

    automation/reports/<YYYY-MM-DD>/<HH-MM-SS>/

The date is the top-level folder (so all of a day's runs sit together);
the time-stamped subfolder holds everything from that one specific run.
"""
import hashlib
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import allure

AUTOMATION_ROOT = Path(__file__).resolve().parent.parent


def get_run_dir() -> Path:
    """
    Returns the current run's folder, creating it once per process.
    Reuses the same folder for the whole pytest session via an
    environment variable, so Allure config and screenshot/trace capture
    all land in the same place.
    """
    existing = os.environ.get("SQA_RUN_DIR")
    if existing:
        return Path(existing)

    now = datetime.now()
    date_folder = now.strftime("%Y-%m-%d")
    time_folder = now.strftime("%H-%M-%S")
    run_dir = AUTOMATION_ROOT / "reports" / date_folder / time_folder

    (run_dir / "screenshots" / "passed").mkdir(parents=True, exist_ok=True)
    (run_dir / "screenshots" / "failed").mkdir(parents=True, exist_ok=True)
    (run_dir / "traces").mkdir(parents=True, exist_ok=True)
    (run_dir / "allure-results").mkdir(parents=True, exist_ok=True)
    (run_dir / "downloads").mkdir(parents=True, exist_ok=True)

    os.environ["SQA_RUN_DIR"] = str(run_dir)
    return run_dir


def short_folder_name(test_name: str) -> str:
    """
    Shortens a long test name so the full file path stays under the Windows
    limit of 260 characters, wherever the project is placed on the computer.
    A short name is returned unchanged. A long name is cut and ends with a
    short code made from the full name, so two long names never clash.
    """
    longest_prefix = len(str(get_run_dir() / "screenshots" / "passed")) + 1
    room_for_name = 250 - longest_prefix - 55
    max_length = max(40, room_for_name)
    if len(test_name) <= max_length:
        return test_name
    code = hashlib.md5(test_name.encode("utf-8")).hexdigest()[:6]
    return f"{test_name[:max_length - 7]}_{code}"


def screenshot_path(test_name: str, step_no: int, description: str) -> str:
    """
    Builds a numbered screenshot path inside the current run folder.

    Every test gets its own sub-folder, and the files are numbered in the
    order they were taken, so the folder reads like a story:

        screenshots/test_export_income_statement_report/
            01_logged_in.png
            02_income_statement_opened.png
            03_filter_popup_filled.png
            ...
    """
    # Make the description safe for a file name: lower case, and every run of other signs
    # (spaces, "/" in a date, ...) becomes one underscore. The cut to 45 characters comes
    # last, so the name never ends with a sign that would split the path.
    clean_description = re.sub(r"[^a-z0-9_-]+", "_", description.strip().lower())[:45].strip("_") or "screenshot"
    test_folder = get_run_dir() / "screenshots" / short_folder_name(test_name)
    test_folder.mkdir(parents=True, exist_ok=True)
    return str(test_folder / f"{step_no:02d}_{clean_description}.png")


def take_numbered_screenshot(page, test_item, description: str) -> str:
    """
    Take a screenshot and number it 01, 02, 03 ... in the order taken.

    The counter is stored on the test itself, so each test starts again at 01.
    Returns the path of the saved file.
    """
    step_no = getattr(test_item, "screenshot_count", 0) + 1
    test_item.screenshot_count = step_no
    # A parametrized test file can give its tests a clean name (see `report_name`
    # in tests/test_02_income_statement.py) so the folder has no [ ] in it.
    path = screenshot_path(getattr(test_item, "report_name", test_item.name), step_no, description)
    page.screenshot(path=path)

    # Also attach it to the Allure report, in the same numbered order
    allure.attach.file(path, name=f"{step_no:02d} {description}", attachment_type=allure.attachment_type.PNG)
    return path


def sort_screenshots_by_result(test_item, failed: bool) -> None:
    """
    Move the test's screenshot folder into screenshots/passed/ or screenshots/failed/.

    Called once, right after the test body and its last screenshot, when the result is
    known. Does nothing when the test took no screenshots.

        screenshots/test_x/  ->  screenshots/passed/test_x/   (or failed/)
    """
    test_name = getattr(test_item, "report_name", test_item.name)
    screenshots_dir = get_run_dir() / "screenshots"
    folder_name = short_folder_name(test_name)
    test_folder = screenshots_dir / folder_name
    if not test_folder.is_dir():
        return
    result_dir = screenshots_dir / ("failed" if failed else "passed")
    result_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(test_folder), str(result_dir / folder_name))


def did_test_fail(test_item) -> bool:
    """Return True if the test body of `test_item` failed (the result is stored by conftest.py)."""
    return getattr(getattr(test_item, "rep_call", None), "failed", False)


def download_path(filename: str) -> str:
    """Builds a path for a downloaded file (e.g. an exported report) inside the current run folder."""
    return str(get_run_dir() / "downloads" / filename)


def trace_path(test_name: str) -> str:
    """Builds a trace file path inside the current run folder."""
    run_dir = get_run_dir()
    return str(run_dir / "traces" / f"{short_folder_name(test_name)}.zip")


def attach_trace_to_report(trace_file: str) -> None:
    """Attach a trace file to the current test in the Allure report, so it can be downloaded from the report."""
    allure.attach.file(trace_file, name="trace.zip (open with: playwright show-trace)", extension="zip")


def write_environment_info(application_url: str, environment: str) -> None:
    """
    Write the "Environment" box shown on the Allure report's Overview page.
    No credentials are written.
    """
    lines = [
        f"Application URL={application_url}",
        f"Environment={environment}",
        "Browser=Chromium (headed, maximized)",
        f"Run started={get_run_dir().parent.name} {get_run_dir().name}",
    ]
    (get_run_dir() / "allure-results" / "environment.properties").write_text("\n".join(lines), encoding="utf-8")


def generate_html_report() -> str | None:
    """
    Build ONE self-contained HTML report from this run's Allure results.

    The file is saved in the run folder as Test_Report_<date>_<time>.html. It
    contains everything (results, screenshots), so it opens by double-click on
    any computer and can be sent by email as it is.

    Returns the path of the report, or None if it could not be created
    (for example when the Allure command-line tool is not installed).
    """
    run_dir = get_run_dir()
    help_text = (
        f"The raw data is kept in {run_dir / 'allure-results'}; build the report from it as described in "
        "automation/HOW_TO_RUN.md > The HTML report > If the report was not created."
    )
    allure_command = shutil.which("allure")
    if allure_command is None:
        print(f"\nHTML report NOT created: the 'allure' command was not found (install Allure and Java). {help_text}")
        return None

    temp_folder = run_dir / "report_temp"
    result = subprocess.run(
        [allure_command, "generate", "--single-file", "--clean", str(run_dir / "allure-results"), "-o", str(temp_folder)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"\nHTML report NOT created. Allure said: {result.stderr.strip() or result.stdout.strip()}\n{help_text}")
        return None

    report_file = run_dir / f"Test_Report_{run_dir.parent.name}_{run_dir.name}.html"
    shutil.move(str(temp_folder / "index.html"), str(report_file))
    shutil.rmtree(temp_folder, ignore_errors=True)
    print(f"\nHTML report: {report_file}")
    return str(report_file)


def trace_one_test(page, test_request):
    """
    Records one trace for a single test when many tests share one logged-in
    browser tab. Use it inside a file's `page` fixture:

        yield from trace_one_test(logged_in_page, request)

    A failed test keeps its trace and it is attached to the report; a passed
    test throws its trace away.
    """
    tracing = page.context.tracing
    tracing.start_chunk()
    yield page
    if did_test_fail(test_request.node):
        trace_file = trace_path(test_request.node.name)
        tracing.stop_chunk(path=trace_file)
        attach_trace_to_report(trace_file)
    else:
        tracing.stop_chunk()

