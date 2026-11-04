"""
conftest.py: the test SET-UP file. pytest loads it automatically.

In plain words:
    This file opens the browser and gives every test a fresh tab already
    pointed at BASE_URL. You never import it and you never call it. A test
    simply asks for what it needs by naming it as a parameter:

        def test_login(login_page):   # <- pytest builds login_page for you

    The name must stay exactly "conftest.py" and the file must stay in the
    automation/ folder, or pytest will not find it. (Reusable helper
    functions that tests DO call yourself live in utils/helpers.py instead.)

What is inside:
- browser fixture:   opens one browser for the whole run.
- page fixture:      a new tab per test; saves a trace if the test failed.
                     Every test also gets a final screenshot (end_of_test_...).
- take_screenshot fixture: numbered step screenshots (01_..., 02_...) in
                     reports/<date>/<time>/screenshots/<test name>/.
- login_page, dashboard_page, finance_dashboard_page, income_statement_page
                     fixtures: page objects, ready to use.
- Allure results are pointed at this run's dated folder (utils/run_context.py).
- Every test writes a START line and an END line (with PASSED / FAILED and
  its duration) to logs/test_run.log, so the log is easy to read test by test.
- At the end of every run, one self-contained HTML report is built in that
  folder: Test_Report_<date>_<time>.html (opens by double-click).
"""
import os
import sys

import pytest
from playwright.sync_api import sync_playwright
from config.settings import BASE_URL, ENVIRONMENT
from test_data.asset_shipment_data import (
    OTHER_BRANCH_DIFFERENT_PROJECT,
    OTHER_BRANCH_SAME_PROJECT,
)
from utils.logger import test_logger
from utils.run_context import (
    attach_trace_to_report,
    generate_html_report,
    get_run_dir,
    did_test_fail,
    sort_screenshots_by_result,
    take_numbered_screenshot,
    trace_path,
    write_environment_info,
)


# How many tests are in this run and how many have started, for the "[3/64]" in the START line
TEST_COUNT = {"total": 0, "started": 0}

# Window size used when the browser runs without a window (--headless)
HEADLESS_WINDOW_SIZE = "--window-size=1920,1080"


def pytest_addoption(parser):
    """Adds the --headless option: run the browser without a window (the default is a visible window)."""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run the browser without a visible window. The log lines still show in the terminal.",
    )
    parser.addoption(
        "--screen-size",
        action="store",
        default="",
        help="Run the browser in a window of this size, for example 1280x720, to test a small screen. "
        "Without it the window is maximized.",
    )


def pytest_configure(config):
    """
    Runs once at session start. Points Allure's output at this run's
    dated folder instead of a fixed top-level allure-results/ directory.
    """
    # Only finding the tests (VS Code does this to show the play buttons): no run folder
    if config.option.collectonly:
        return
    run_dir = get_run_dir()
    config.option.allure_report_dir = str(run_dir / "allure-results")
    write_environment_info(BASE_URL, ENVIRONMENT)
    test_logger.info(f"========== START RUN {run_dir.parent.name} {run_dir.name} | Python: {sys.executable} ==========")
    # The window helper below reads this to know there is no window to maximize
    os.environ["SQA_HEADLESS"] = "1" if config.getoption("--headless") else ""
    # The same for the chosen screen size, for example "1280x720" (empty means maximized)
    os.environ["SQA_SCREEN_SIZE"] = config.getoption("--screen-size")


def pytest_collection_finish(session):
    """
    Remembers how many tests will run, for the "[3/64]" count in the START line.
    """
    TEST_COUNT["total"] = len(session.items)


def pytest_runtest_logstart(nodeid, location):
    """Writes a START line to the log when a test begins, so the log shows where each test starts."""
    TEST_COUNT["started"] += 1
    position = f"[{TEST_COUNT['started']}/{TEST_COUNT['total']}]"
    test_logger.info(f"========== START {position}: {nodeid.split('::')[-1]} ==========")


def read_reason(report) -> str:
    """Return the reason of a failed or skipped test report as one short line."""
    if report.skipped:
        reason = report.longrepr[2] if isinstance(report.longrepr, tuple) else str(report.longrepr)
    else:
        crash = getattr(report.longrepr, "reprcrash", None)
        reason = crash.message if crash else str(report.longrepr)
    return " ".join(reason.split())[:600]


def pytest_runtest_logreport(report):
    """
    Writes an END line to the log when a test finishes, with its result and
    how long it took. A test that could not even start (set-up error) is
    reported as ERROR. A failed test is logged as ERROR and a skipped test as
    WARNING, each with its reason on the next line; a passed test is INFO.
    """
    test_finished = report.when == "call"
    test_could_not_start = report.when == "setup" and report.failed
    test_skipped_before_start = report.when == "setup" and report.skipped
    if not (test_finished or test_could_not_start or test_skipped_before_start):
        return

    test_name = report.nodeid.split("::")[-1]
    if test_could_not_start:
        result = "ERROR (set-up failed)"
    elif report.skipped:
        result = "SKIPPED"
    else:
        result = "FAILED" if report.failed else "PASSED"
    end_line = f"========== END: {test_name} - {result} in {report.duration:.1f} seconds =========="

    if report.failed:
        test_logger.error(end_line)
        test_logger.error(f"Reason: {read_reason(report)}")
    elif report.skipped:
        test_logger.warning(end_line)
        test_logger.warning(f"Reason: {read_reason(report)}")
    else:
        test_logger.info(end_line)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Runs once at the end of the session: builds the single-file HTML report."""
    if session.config.option.collectonly:
        return
    generate_html_report()


@pytest.fixture(scope="session")
def browser(request):
    """
    One browser instance shared across the whole test session.

    - By default the browser window is VISIBLE, so you can watch the test, and
      it opens maximized at the full size of whatever screen this code runs on.
    - With --headless there is no window; the page gets a 1920 x 1080 size.
    - With --screen-size 1280x720 the window has exactly that size (a small screen).
    """
    headless = request.config.getoption("--headless")
    screen_size = request.config.getoption("--screen-size")
    window_arg = HEADLESS_WINDOW_SIZE if headless else "--start-maximized"
    if screen_size:
        width, height = read_screen_size(screen_size)
        window_arg = f"--window-size={width},{height}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=[window_arg])
        yield browser
        browser.close()


def read_screen_size(text: str) -> tuple:
    """Turn a size such as "1280x720" into (1280, 720)."""
    width, height = text.lower().split("x")
    return int(width), int(height)


def maximize_window(context, page) -> None:
    """
    Maximize the browser window that holds `page`, so every screen opens at
    the full size of the monitor. Each new browser context opens its own
    window, so this runs for every tab we create (Chromium only). With
    --screen-size the window gets that size instead (a small screen). With
    --headless there is no window, so nothing is done.
    """
    if os.environ.get("SQA_HEADLESS"):
        return
    bounds = {"windowState": "maximized"}
    screen_size = os.environ.get("SQA_SCREEN_SIZE")
    if screen_size:
        width, height = read_screen_size(screen_size)
        bounds = {"windowState": "normal", "left": 0, "top": 0, "width": width, "height": height}
    cdp_session = context.new_cdp_session(page)
    window = cdp_session.send("Browser.getWindowForTarget")
    cdp_session.send("Browser.setWindowBounds", {"windowId": window["windowId"], "bounds": bounds})
    cdp_session.detach()


@pytest.fixture
def page(browser, request):
    """
    A fresh page per test, already navigated to BASE_URL, with tracing
    enabled so a trace lands in this run's traces/ folder on failure. A
    screenshot is captured either way into this run's screenshots/.
    """
    # Open the page at the full size of the maximized browser window.
    context = browser.new_context(no_viewport=True)
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(BASE_URL)

    yield page

    if did_test_fail(request.node):
        trace_file = trace_path(request.node.name)
        context.tracing.stop(path=trace_file)
        attach_trace_to_report(trace_file)
    else:
        context.tracing.stop()

    context.close()


@pytest.fixture
def take_screenshot(page, request):
    """
    Gives a test a function to take numbered screenshots at important steps:

        take_screenshot("filter popup filled")   ->  03_filter_popup_filled.png

    Use a short description of what the screen shows at that moment.
    """
    def _take(description: str) -> str:
        return take_numbered_screenshot(page, request.node, description)
    return _take


@pytest.fixture(scope="module")
def hofin_flow_data():
    """
    A dictionary shared by the tests of one file, so a test can leave a value
    (for example the parent asset serial) for the next test:

        hofin_flow_data["parent_serial"] = parent_serial
    """
    return {}


@pytest.fixture
def hofin_flow(browser, request):
    """
    The HOFIN > HOFA > HOFIN asset flow (utils/hofin_flow.py). Each stage opens
    its own browser window for its own login. Windows kept open for the test
    (the HOFA Global List) are closed at the end of the test.
    """
    from utils.hofin_flow import HofinAssetFlow

    flow = HofinAssetFlow(browser, request.node, maximize_window)
    yield flow
    flow.close_all()


@pytest.fixture(scope="session")
def hofin_asset_records():
    """
    The HOFIN assets made during this run, shared by every test file, so each one is
    registered only once per run. Used by `hofin_assets`; nothing is saved between runs.
    """
    return {}


@pytest.fixture
def hofin_assets(hofin_flow, hofin_asset_records):
    """
    Registers assets through HOFIN > HOFA > HOFIN and returns their real serials
    (utils/hofin_assets.py). It works beside the AAQ `registrations` / `assets`:
        serial = hofin_assets.get_normal_asset()["serial"]
        pair = hofin_assets.get_parent_with_extended()   # {"parent": ..., "extended": [...]}
    """
    from utils.hofin_assets import HofinAssets

    return HofinAssets(hofin_flow, hofin_asset_records)


@pytest.fixture
def hofin_normal_asset(hofin_assets):
    """The run's normal asset registered in HOFIN (no extended asset): {"serial": ..., "transaction_no": ..., ...}."""
    return hofin_assets.get_normal_asset()


@pytest.fixture
def hofin_parent_with_extended(hofin_assets):
    """The run's parent asset registered in HOFIN with two extended assets: {"parent": ..., "extended": [...], ...}."""
    return hofin_assets.get_parent_with_extended()


@pytest.fixture(scope="module")
def hofa_logged_in_page(browser):
    """
    One HOFA tab (HOFA_URL) signed in ONCE as the HOFA acknowledger (HOFA_ACK_USERNAME
    in .env) and shared by every test in the same file. The Asset Profile screens of
    HOFIN assets are checked as this user. A test file uses it by overriding `page`.
    """
    from config.settings import HOFA_ACK_PASSWORD, HOFA_ACK_USERNAME, HOFA_URL

    assert HOFA_ACK_USERNAME and HOFA_ACK_PASSWORD and HOFA_URL, (
        "HOFA_URL, HOFA_ACK_USERNAME and HOFA_ACK_PASSWORD must be set in .env (see .env.example)."
    )
    context = browser.new_context(no_viewport=True)
    # Tracing is started so the test file can record one trace chunk per test
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(HOFA_URL)
    sign_in(page, HOFA_ACK_USERNAME, HOFA_ACK_PASSWORD, "")

    yield page

    context.tracing.stop()
    context.close()


@pytest.fixture(scope="session")
def extended_asset_pairs():
    """
    The parent assets with extended assets made during this run, shared by every
    test file, so each pair is made only once per run. Tests read it through
    `parent_with_extended`; nothing is saved between runs.
    """
    return {}


@pytest.fixture
def parent_with_extended(hofin_assets, extended_asset_pairs):
    """
    A new parent asset with one extended asset (CR FAHOV2-643), as
    {"parent": serial, "extended": serial}. The first test of a run that asks for it
    makes it through HOFIN, HOFA and HOFIN (a few minutes); later tests reuse it.
    """
    if extended_asset_pairs.get("one_extended_error"):
        pytest.fail(f"The parent asset with an extended asset could not be made earlier in this run: {extended_asset_pairs['one_extended_error']}")
    if "one_extended" not in extended_asset_pairs:
        try:
            pair = hofin_assets.register_parent_with_extended(1)
        except Exception as error:
            extended_asset_pairs["one_extended_error"] = str(error).splitlines()[0]
            raise
        extended_asset_pairs["one_extended"] = {"parent": pair["parent"], "extended": pair["extended"][0]}
    return extended_asset_pairs["one_extended"]


@pytest.fixture
def assigned_parent_with_extended(
    page, parent_with_extended, assign_page, transaction_approval_page, asset_serial_global_list_page,
):
    """
    The parent asset and its extended asset of `parent_with_extended`, ASSIGNED to the HOFA
    acknowledger and acknowledged, which is the state Asset Internal Movement needs (an asset
    with an acknowledgement pending is not offered there). It does only the missing steps:
    assign and approve when the parent is UNASSIGNED, then acknowledge when an acknowledgement
    waits. Works in the test file's `page` tab (the HOFA acknowledger). Returns the same
    dictionary as `parent_with_extended`.
    """
    from pages.asset_assign_acknowledgement_page import AssetAssignAcknowledgementPage
    from test_data.asset_transaction_data import UNASSIGNED
    from test_data.hofin_asset_data import HOFA_ACK_EMPLOYEE_PIN
    from test_data.toast_messages import ACKNOWLEDGE_TOAST
    from utils.asset_flow import assign_and_approve

    parent_serial = parent_with_extended["parent"]
    status = asset_serial_global_list_page.open_and_read_assign_status(parent_serial)
    if status == UNASSIGNED:
        assign_and_approve(
            assign_page, transaction_approval_page, parent_serial, HOFA_ACK_EMPLOYEE_PIN, "AUTOMATION_TEST setup assign"
        )
    acknowledgement_page = AssetAssignAcknowledgementPage(page)
    acknowledgement_page.navigate_here()
    # One pass over the pending rows: when the parent's row is found its Details popup stays open
    if acknowledgement_page.find_pending_row_with_serial(parent_serial) >= 0:
        toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
        acknowledgement_page.verify_toast_contains(toast, ACKNOWLEDGE_TOAST, "Acknowledge in the setup")
    return parent_with_extended


@pytest.fixture
def parent_with_inactive_extended(
    hofin_assets, extended_asset_pairs, asset_serial_global_list_page, asset_write_off_page,
    asset_write_off_list_page, asset_write_off_approval_list_page,
):
    """
    A new parent asset with three extended assets, the third written off so it is
    inactive (CR FAHOV2-643), as {"parent": serial, "active": [first two], "inactive": third}.
    The first test of a run that asks for it makes it (several minutes); later tests reuse it.
    """
    from test_data.hofin_asset_data import WRITE_OFF_PROJECT
    from utils.write_off_flow import write_off_one_asset

    if "inactive_extended" not in extended_asset_pairs:
        pair = hofin_assets.register_parent_with_extended(3)
        parent, extended_serials = pair["parent"], pair["extended"]
        write_off_one_asset(
            asset_serial_global_list_page, asset_write_off_page, asset_write_off_list_page,
            asset_write_off_approval_list_page, extended_serials[2], WRITE_OFF_PROJECT,
        )
        extended_asset_pairs["inactive_extended"] = {
            "parent": parent, "active": extended_serials[:2], "inactive": extended_serials[2],
        }
    return extended_asset_pairs["inactive_extended"]


@pytest.fixture
def assets_pending_acknowledgement(
    hofin_assets, extended_asset_pairs, asset_serial_global_list_page, asset_write_off_page,
    asset_write_off_list_page, asset_write_off_approval_list_page, assign_page, transaction_approval_page,
):
    """
    One approved assignment waiting for acknowledgement (CR FAHOV2-643 F07S01). It holds a new
    parent asset with three extended assets, the third written off (inactive), and a new normal
    asset with no extended asset, all assigned in ONE transaction to the HOFA acknowledger:
        {"parent": serial, "active": [first two], "inactive": third, "normal": serial}
    Made once per run (about 15 minutes). When making it fails, every later test that asks
    for it fails at once with the same reason instead of making it again.
    """
    from test_data.hofin_asset_data import HOFA_ACK_EMPLOYEE_PIN, WRITE_OFF_PROJECT
    from utils.asset_flow import assign_several_and_approve
    from utils.write_off_flow import write_off_one_asset

    key = "pending_acknowledgement"
    if extended_asset_pairs.get(key + "_error"):
        pytest.fail(f"The assets for this test could not be made earlier in this run: {extended_asset_pairs[key + '_error']}")
    if key not in extended_asset_pairs:
        try:
            pair = hofin_assets.register_parent_with_extended(3)
            write_off_one_asset(
                asset_serial_global_list_page, asset_write_off_page, asset_write_off_list_page,
                asset_write_off_approval_list_page, pair["extended"][2], WRITE_OFF_PROJECT,
            )
            normal = hofin_assets.register_normal_asset()["serial"]
            assign_several_and_approve(
                assign_page, transaction_approval_page, [pair["parent"], normal],
                HOFA_ACK_EMPLOYEE_PIN, "AUTOMATION_TEST assign for acknowledgement",
            )
        except Exception as error:
            extended_asset_pairs[key + "_error"] = str(error).splitlines()[0]
            raise
        extended_asset_pairs[key] = {
            "parent": pair["parent"], "active": pair["extended"][:2], "inactive": pair["extended"][2], "normal": normal,
        }
    return extended_asset_pairs[key]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Stashes the test result on the item so the `page` fixture can tell,
    during its own teardown, whether the test passed or failed.

    Also takes the last screenshot of every test, right after the test body
    finishes: the screen as it was at the end, numbered after the screenshots
    the test took itself. It is attached to the report inside the test body.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    if rep.when == "call":
        page = item.funcargs.get("page")
        if page is not None:
            description = "end_of_test_FAILED" if rep.failed else "end_of_test_passed"
            take_numbered_screenshot(page, item, description)
        sort_screenshots_by_result(item, rep.failed)


@pytest.fixture
def login_page(page):
    """Login page object, ready to use in any test."""
    from pages.login_page import LoginPage
    return LoginPage(page)


@pytest.fixture(scope="module")
def logged_in_page(browser, request):
    """
    One browser tab that logs in ONCE and is then shared by every test in the
    same test file. Use it in a test file whose tests all need a logged-in user:
    the file overrides the `page` fixture to return this tab (see
    tests/test_01_asset_registration_aaq.py).

    Tracing is started here. The test file starts and stops one trace chunk
    per test (see `trace_one_test` in utils/run_context.py).
    """
    from config.settings import DEFAULT_BRANCH, ERP_PASSWORD, ERP_USERNAME

    # Open the page at the full size of the maximized browser window.
    context = browser.new_context(no_viewport=True)
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(BASE_URL)
    sign_in(page, ERP_USERNAME, ERP_PASSWORD, DEFAULT_BRANCH)

    yield page

    context.tracing.stop()
    context.close()


def sign_in(page, username: str, password: str, branch: str) -> None:
    """
    Sign in on a tab that shows the sign-in screen: stop with a clear reason if
    the login failed, choose the user's office when the ERP asks for one, close
    the advertisement popup if it appears, and remember which user this tab is.
    """
    from pages.login_page import LoginPage
    from utils.login_session import remember_user

    login_page = LoginPage(page)
    login_page.wait_for_login_page()
    login_page.login(username, password)
    login_page.verify_logged_in(username)
    login_page.select_office_if_asked(branch)
    login_page.close_popup_if_present()
    remember_user(page, username, password, branch)


@pytest.fixture(scope="module")
def assignee_logged_in_page(browser):
    """
    A second browser tab signed in as the second user (ASSIGN_ERP_USERNAME in
    .env), shared by every test in the same file. It is the employee an asset is
    assigned to, who is the only user that can acknowledge the assignment. It
    lives in its own browser context, so it never shares a session with the main
    user's tab. The tests are skipped when the second user is not set in .env.
    """
    from config.settings import ASSIGN_DEFAULT_BRANCH, ASSIGN_ERP_PASSWORD, ASSIGN_ERP_USERNAME

    from config.settings import ERP_USERNAME

    if not ASSIGN_ERP_USERNAME or not ASSIGN_ERP_PASSWORD:
        pytest.skip("ASSIGN_ERP_USERNAME and ASSIGN_ERP_PASSWORD are not set in .env")
    # The ERP allows one login per user, so a second tab with the same user would log the first one out
    assert ASSIGN_ERP_USERNAME != ERP_USERNAME, (
        "ASSIGN_ERP_USERNAME is the same user as ERP_USERNAME. The ERP does not allow two logins "
        "of one user at the same time: use a different user for the employee who acknowledges."
    )

    context = browser.new_context(no_viewport=True)
    # Tracing is started so a test file that works only in this tab can record one trace chunk per test
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(BASE_URL)
    sign_in(page, ASSIGN_ERP_USERNAME, ASSIGN_ERP_PASSWORD, ASSIGN_DEFAULT_BRANCH)

    yield page

    context.tracing.stop()
    context.close()


@pytest.fixture
def aaq_page(page):
    """Asset Registration by AAQ page object, ready to use."""
    from pages.asset_registration_aaq_page import AssetRegistrationAaqPage
    return AssetRegistrationAaqPage(page)


@pytest.fixture
def registration_list_page(page):
    """Asset Registration List page object, ready to use."""
    from pages.asset_registration_list_page import AssetRegistrationListPage
    return AssetRegistrationListPage(page)


@pytest.fixture
def approval_list_page(page):
    """Asset Registration Approval List page object, ready to use."""
    from pages.asset_registration_approval_list_page import AssetRegistrationApprovalListPage
    return AssetRegistrationApprovalListPage(page)


@pytest.fixture
def asset_serial_global_list_page(page):
    """Asset Serial Global List page object, ready to use."""
    from pages.asset_serial_global_list_page import AssetSerialGlobalListPage
    return AssetSerialGlobalListPage(page)


@pytest.fixture
def generate_barcode_page(page):
    """Generate Barcode page object, ready to use."""
    from pages.generate_barcode_page import GenerateBarcodePage
    return GenerateBarcodePage(page)


@pytest.fixture
def pending_process_list_page(page):
    """Asset In Pending Process List page object, ready to use."""
    from pages.asset_in_pending_process_list_page import AssetInPendingProcessListPage
    return AssetInPendingProcessListPage(page)


@pytest.fixture
def asset_serial_split_page(page):
    """Asset Serial Split page object, ready to use."""
    from pages.asset_serial_split_page import AssetSerialSplitPage
    return AssetSerialSplitPage(page)


@pytest.fixture
def asset_split_list_page(page):
    """Asset Serial Split List page object, ready to use."""
    from pages.asset_serial_split_list_page import AssetSerialSplitListPage
    return AssetSerialSplitListPage(page)


@pytest.fixture
def asset_split_approval_list_page(page):
    """Asset Serial Split Approval List page object, ready to use."""
    from pages.asset_serial_split_approval_list_page import AssetSerialSplitApprovalListPage
    return AssetSerialSplitApprovalListPage(page)


@pytest.fixture
def splits(
    registrations, asset_serial_split_page, asset_split_list_page,
    asset_split_approval_list_page, shared_registrations,
):
    """
    Gives a test the saved Land asset's split in a chosen state:
        splits.get_pending_split()
    It returns the split an earlier test made, or performs / approves it now
    when the test runs on its own. See utils/split_helper.py.
    """
    from utils.split_helper import SplitHelper

    return SplitHelper(
        registrations, asset_serial_split_page, asset_split_list_page,
        asset_split_approval_list_page, shared_registrations,
    )


@pytest.fixture
def shipment_page(page):
    """Asset Shipment page object (the logged-in user's tab), ready to use."""
    from pages.asset_shipment_page import AssetShipmentPage
    return AssetShipmentPage(page)


@pytest.fixture
def challan_page(page):
    """Transfer Challan page object (the Challan tab and popups of a shipment), ready to use."""
    from pages.shipment_challan_page import ShipmentChallanPage
    return ShipmentChallanPage(page)


@pytest.fixture
def challan_approval_page(page):
    """Asset Shipment Challan Approval List page object, ready to use."""
    from pages.shipment_challan_approval_page import ShipmentChallanApprovalPage
    return ShipmentChallanApprovalPage(page)


@pytest.fixture
def in_challan_page(page):
    """Asset Shipment In-Challan page object, ready to use."""
    from pages.shipment_in_challan_page import ShipmentInChallanPage
    return ShipmentInChallanPage(page)


@pytest.fixture
def gate_pass_page(page):
    """Gate Pass Generation page object, ready to use."""
    from pages.gate_pass_page import GatePassPage
    return GatePassPage(page)


@pytest.fixture(scope="session")
def shared_transfer():
    """
    The Asset Shipment flow of this run (shipment, challan, serial, ...), shared
    by every test file so one test can reuse what an earlier test did. Used by
    the `transfer` fixture below; tests do not read it directly.
    """
    return {}


@pytest.fixture
def transfer(
    assets, shipment_page, challan_page, challan_approval_page, in_challan_page, shared_transfer
):
    """
    Carries one Asset Shipment through its stages:
        flow = transfer.reach("draft_challan")
    It returns what an earlier test did, or does the missing stages now when
    the test runs on its own. See utils/transfer_helper.py.
    """
    from utils.transfer_helper import TransferHelper

    return TransferHelper(
        assets, shipment_page, challan_page,
        challan_approval_page, in_challan_page, shared_transfer,
    )


@pytest.fixture(scope="module")
def ack_shipment_logged_in_page(browser):
    """
    A browser tab signed in as the shipment acknowledgement user (ACK_SHIPMENT_ERP_* in
    .env), shared by every test in the same file. Its default branch is the receiving
    branch of the shipment, so it is the user who sees the challan and acknowledges it.
    It lives in its own browser context. The tests are skipped when the user is not set.
    """
    from config.settings import (
        ACK_SHIPMENT_ERP_DEFAULT_BRANCH,
        ACK_SHIPMENT_ERP_PASSWORD,
        ACK_SHIPMENT_ERP_USERNAME,
        ERP_USERNAME,
    )

    if not ACK_SHIPMENT_ERP_USERNAME or not ACK_SHIPMENT_ERP_PASSWORD:
        pytest.skip("ACK_SHIPMENT_ERP_USERNAME and ACK_SHIPMENT_ERP_PASSWORD are not set in .env")
    # The ERP allows one login per user, so a second tab with the same user would log the first one out
    assert ACK_SHIPMENT_ERP_USERNAME != ERP_USERNAME, (
        "ACK_SHIPMENT_ERP_USERNAME is the same user as ERP_USERNAME. The ERP does not allow two logins "
        "of one user at the same time: use a different user for the receiving branch."
    )

    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(BASE_URL)
    sign_in(page, ACK_SHIPMENT_ERP_USERNAME, ACK_SHIPMENT_ERP_PASSWORD, ACK_SHIPMENT_ERP_DEFAULT_BRANCH)

    yield page

    context.close()


@pytest.fixture
def ack_in_challan_page(ack_shipment_logged_in_page):
    """Asset Shipment In-Challan page object in the shipment acknowledgement user's tab."""
    from pages.shipment_in_challan_page import ShipmentInChallanPage
    return ShipmentInChallanPage(ack_shipment_logged_in_page)


@pytest.fixture
def take_ack_shipment_screenshot(ack_shipment_logged_in_page, request):
    """Like `take_screenshot`, but photographs the shipment acknowledgement user's tab (`take_screenshot` shows the main tab)."""
    def _take(description: str) -> str:
        return take_numbered_screenshot(ack_shipment_logged_in_page, request.node, f"receiving user {description}")
    return _take


@pytest.fixture(scope="session")
def shared_cross_transfer():
    """The Asset Shipment flows to another branch of this run, one per scenario (used by `cross_transfer`)."""
    return {}


def build_cross_transfer(
    scenario, assets, shipment_page, challan_page, challan_approval_page, in_challan_page,
    ack_in_challan_page, shared_cross_transfer,
):
    """Return the TransferHelper of one scenario of a shipment to another branch (see utils/transfer_helper.py)."""
    from utils.transfer_helper import TransferHelper

    flows = shared_cross_transfer.setdefault(scenario, {})
    return TransferHelper(
        assets, shipment_page, challan_page, challan_approval_page, in_challan_page,
        flows, scenario, ack_in_challan_page,
    )


@pytest.fixture
def transfer_other_branch_same_project(
    assets, shipment_page, challan_page, challan_approval_page, in_challan_page,
    ack_in_challan_page, shared_cross_transfer,
):
    """
    Like `transfer`, for a shipment to another branch with the same From and To Project. The
    sender's tab creates and approves; the receiving user's tab (ACK_SHIPMENT_ERP_* in .env)
    sees and acknowledges the challan.
    """
    return build_cross_transfer(
        OTHER_BRANCH_SAME_PROJECT, assets, shipment_page, challan_page, challan_approval_page,
        in_challan_page, ack_in_challan_page, shared_cross_transfer,
    )


@pytest.fixture
def transfer_other_branch_different_project(
    assets, shipment_page, challan_page, challan_approval_page, in_challan_page,
    ack_in_challan_page, shared_cross_transfer,
):
    """Like `transfer_other_branch_same_project`, but the To Project is different from the From Project."""
    return build_cross_transfer(
        OTHER_BRANCH_DIFFERENT_PROJECT, assets, shipment_page, challan_page, challan_approval_page,
        in_challan_page, ack_in_challan_page, shared_cross_transfer,
    )


@pytest.fixture
def assign_page(page):
    """Asset Assign page object, ready to use."""
    from pages.asset_assign_page import AssetAssignPage
    return AssetAssignPage(page)


@pytest.fixture
def unassign_page(page):
    """Asset Un Assign page object, ready to use."""
    from pages.asset_unassign_page import AssetUnassignPage
    return AssetUnassignPage(page)


@pytest.fixture
def internal_movement_page(page):
    """Asset Internal Movement page object, ready to use."""
    from pages.asset_internal_movement_page import AssetInternalMovementPage
    return AssetInternalMovementPage(page)


@pytest.fixture
def transactions(
    assets, assign_page, unassign_page, internal_movement_page,
    transaction_approval_page, asset_serial_global_list_page,
):
    """
    Gives a test a usage asset (usage_a by default, or usage_b) in the state it needs:
        serial = transactions.ensure_assigned()
        serial = transactions.ensure_assigned("usage_b")
    It reads the asset's real Assign Status and does only the missing steps.
    See utils/transaction_helper.py.
    """
    from utils.transaction_helper import TransactionHelper

    return TransactionHelper(
        assets, assign_page, unassign_page, internal_movement_page,
        transaction_approval_page, asset_serial_global_list_page,
    )


@pytest.fixture
def transaction_list_page(page):
    """Transaction List page object, ready to use."""
    from pages.transaction_list_page import TransactionListPage
    return TransactionListPage(page)


@pytest.fixture
def transaction_approval_page(page):
    """Transaction Approval List page object, ready to use."""
    from pages.transaction_approval_list_page import TransactionApprovalListPage
    return TransactionApprovalListPage(page)


@pytest.fixture(scope="session")
def shared_registrations():
    """
    The registrations created during this run, shared by every test file, so
    one test can reuse what another created (see utils/run_registrations.py).
    Used by the `registrations` fixture below; tests do not read it directly.
    Nothing is saved between runs.
    """
    from utils.run_registrations import RunRegistrations

    return RunRegistrations()


@pytest.fixture
def registrations(aaq_page, registration_list_page, approval_list_page, shared_registrations):
    """
    Gives a test a registration of a chosen item in a chosen status:
        registrations.get_pending("land")
    It returns one an earlier test made, or creates one when the test runs on
    its own. See utils/registration_helper.py.
    """
    from utils.registration_helper import RegistrationHelper

    return RegistrationHelper(
        aaq_page, registration_list_page, approval_list_page, shared_registrations
    )


@pytest.fixture
def acknowledgement_page(assignee_logged_in_page):
    """Asset Assign Acknowledgement page object. It works in the second user's tab: only the assigned employee can acknowledge."""
    from pages.asset_assign_acknowledgement_page import AssetAssignAcknowledgementPage
    return AssetAssignAcknowledgementPage(assignee_logged_in_page)


@pytest.fixture
def take_assignee_screenshot(assignee_logged_in_page, request):
    """
    Like `take_screenshot`, but photographs the second user's tab. `take_screenshot`
    always shows the main tab, so a test that works in both tabs needs this one for the second.
    """
    def _take(description: str) -> str:
        return take_numbered_screenshot(assignee_logged_in_page, request.node, f"assignee {description}")
    return _take


@pytest.fixture
def expense_page(page):
    """Asset Expense page object, ready to use."""
    from pages.asset_expense_page import AssetExpensePage
    return AssetExpensePage(page)


@pytest.fixture
def expense_approval_page(page):
    """Asset Expense Approval page object, ready to use."""
    from pages.asset_expense_approval_page import AssetExpenseApprovalPage
    return AssetExpenseApprovalPage(page)


@pytest.fixture
def expenses(assets, expense_page, expense_approval_page, shared_registrations):
    """
    Gives an Asset Expense test a usage asset and an approved expense:
        serial = expenses.get_serial()
        record = expenses.get_approved_expense("Inventory")
    It returns what an earlier test made, or makes it when the test runs on its
    own. See utils/expense_helper.py.
    """
    from utils.expense_helper import ExpenseHelper

    return ExpenseHelper(assets, expense_page, expense_approval_page, shared_registrations)


@pytest.fixture
def voucher_search_page(page):
    """Accounting Voucher Search page object, ready to use."""
    from pages.voucher_search_page import VoucherSearchPage
    return VoucherSearchPage(page)


@pytest.fixture
def asset_write_off_page(page):
    """Asset Write-off page object, ready to use."""
    from pages.asset_write_off_page import AssetWriteOffPage
    return AssetWriteOffPage(page)


@pytest.fixture
def asset_write_off_list_page(page):
    """Asset Write-off List page object, ready to use."""
    from pages.asset_write_off_list_page import AssetWriteOffListPage
    return AssetWriteOffListPage(page)


@pytest.fixture
def asset_write_off_approval_list_page(page):
    """Asset Write-off Approval List page object, ready to use."""
    from pages.asset_write_off_approval_list_page import AssetWriteOffApprovalListPage
    return AssetWriteOffApprovalListPage(page)


@pytest.fixture
def asset_sale_page(page):
    """Asset Sale page object, ready to use."""
    from pages.asset_sale_page import AssetSalePage
    return AssetSalePage(page)


@pytest.fixture
def asset_sale_list_page(page):
    """Asset Sale List page object, ready to use."""
    from pages.asset_sale_list_page import AssetSaleListPage
    return AssetSaleListPage(page)


@pytest.fixture
def asset_sale_approval_list_page(page):
    """Asset Sale Approval List page object, ready to use."""
    from pages.asset_sale_approval_list_page import AssetSaleApprovalListPage
    return AssetSaleApprovalListPage(page)


@pytest.fixture
def single_out_challan_page(page):
    """Asset Single Out Challan page object (the logged-in user's tab), ready to use."""
    from pages.single_out_challan_page import SingleOutChallanPage
    return SingleOutChallanPage(page)


@pytest.fixture
def single_out_challan_approval_list_page(page):
    """Asset Single Out Challan Approval List page object (the logged-in user's tab), ready to use."""
    from pages.single_out_challan_approval_list_page import SingleOutChallanApprovalListPage
    return SingleOutChallanApprovalListPage(page)


@pytest.fixture
def single_in_challan_page(page):
    """Asset Single In-Challan page object (the logged-in user's tab), ready to use."""
    from pages.single_in_challan_page import SingleInChallanPage
    return SingleInChallanPage(page)


@pytest.fixture
def single_gate_pass_page(page):
    """Single Challan Gate Pass Generation page object (the logged-in user's tab), ready to use."""
    from pages.single_gate_pass_page import SingleGatePassPage
    return SingleGatePassPage(page)


@pytest.fixture(scope="session")
def shared_single_challan():
    """
    The Single Challan flows of this run (the "draft" and the "submit" challan),
    shared by every test file so one test can reuse what an earlier test did.
    Used by the `single_challan` fixture; tests do not read it directly.
    """
    return {}


@pytest.fixture
def single_challan(
    assets, single_out_challan_page, single_out_challan_approval_list_page, single_in_challan_page,
    shared_single_challan,
):
    """
    Carries a Single Challan through its stages:
        flow = single_challan.reach("submit", "serial_added")
    It returns what an earlier test did, or does the missing stages now when
    the test runs on its own. See utils/single_challan_flow.py.
    """
    from utils.single_challan_flow import SingleChallanFlow

    return SingleChallanFlow(
        assets, single_out_challan_page, single_out_challan_approval_list_page,
        single_in_challan_page, shared_single_challan,
    )


@pytest.fixture
def ack_single_in_challan_page(ack_shipment_logged_in_page):
    """Asset Single In-Challan page object in the receiving-branch user's tab (ACK_SHIPMENT_ERP_* in .env)."""
    from pages.single_in_challan_page import SingleInChallanPage
    return SingleInChallanPage(ack_shipment_logged_in_page)


@pytest.fixture(scope="session")
def shared_cross_single_challan():
    """The Single Challan flows to another branch of this run, one per scenario (used by the single_challan_other_branch_* fixtures)."""
    return {}


def build_cross_single_challan(
    scenario, assets, single_out_challan_page, single_out_challan_approval_list_page,
    single_in_challan_page, ack_single_in_challan_page, shared_cross_single_challan,
):
    """Return the SingleChallanFlow of one scenario of a challan to another branch (see utils/single_challan_flow.py)."""
    from utils.single_challan_flow import SingleChallanFlow

    flows = shared_cross_single_challan.setdefault(scenario, {})
    return SingleChallanFlow(
        assets, single_out_challan_page, single_out_challan_approval_list_page,
        single_in_challan_page, flows, scenario, ack_single_in_challan_page,
    )


@pytest.fixture
def single_challan_other_branch_same_project(
    assets, single_out_challan_page, single_out_challan_approval_list_page,
    single_in_challan_page, ack_single_in_challan_page, shared_cross_single_challan,
):
    """
    Like `single_challan`, for a challan to another branch with the same From and To Project. The
    sender's tab creates and approves; the receiving user's tab (ACK_SHIPMENT_ERP_* in .env) sees
    the challan. Use the "submit" path.
    """
    return build_cross_single_challan(
        OTHER_BRANCH_SAME_PROJECT, assets, single_out_challan_page, single_out_challan_approval_list_page,
        single_in_challan_page, ack_single_in_challan_page, shared_cross_single_challan,
    )


@pytest.fixture
def single_challan_other_branch_different_project(
    assets, single_out_challan_page, single_out_challan_approval_list_page,
    single_in_challan_page, ack_single_in_challan_page, shared_cross_single_challan,
):
    """Like `single_challan_other_branch_same_project`, but the To Project is different from the From Project."""
    return build_cross_single_challan(
        OTHER_BRANCH_DIFFERENT_PROJECT, assets, single_out_challan_page, single_out_challan_approval_list_page,
        single_in_challan_page, ack_single_in_challan_page, shared_cross_single_challan,
    )


@pytest.fixture(scope="session")
def shared_asset_pool():
    """
    The assets of this run by slot (test_data/asset_slots.py), shared by every test file so a
    flow can reuse the asset an earlier flow left. Used by the `assets` fixture; tests do not read it directly.
    """
    return {}


@pytest.fixture
def assets(registrations, asset_serial_global_list_page, pending_process_list_page, shared_asset_pool):
    """
    The asset pool: hands out the approved asset of a slot, registering and approving one
    when it does not exist yet:
        serial = assets.get("sale_profit_a")["serial"]
        assets.consume("sale_profit_a")      # after a flow used the asset up
    See utils/asset_pool.py and test_data/asset_slots.py.
    """
    from utils.asset_pool import AssetPool

    return AssetPool(registrations, asset_serial_global_list_page, pending_process_list_page, shared_asset_pool)


@pytest.fixture(scope="session")
def shared_write_off():
    """The Write-off flows of this run (the "draft" and the "submit" path), shared by every test file. Used by the `write_off` fixture."""
    return {}


@pytest.fixture
def write_off(
    assets, asset_serial_global_list_page, asset_write_off_page, asset_write_off_list_page,
    asset_write_off_approval_list_page, shared_write_off,
):
    """
    Carries an Asset Write-off through its stages:
        flow = write_off.reach("draft", "submitted")
    It returns what an earlier test did, or does the missing stages now when the test runs
    on its own. See utils/write_off_flow.py.
    """
    from utils.write_off_flow import WriteOffFlow

    return WriteOffFlow(
        assets, asset_serial_global_list_page, asset_write_off_page, asset_write_off_list_page,
        asset_write_off_approval_list_page, shared_write_off,
    )


@pytest.fixture(scope="session")
def shared_sale():
    """The Asset Sale flows of this run (profit_a, profit_b, loss_a, loss_b), shared by every test file. Used by the `sale` fixture."""
    return {}


@pytest.fixture
def sale(assets, asset_sale_page, asset_sale_list_page, shared_sale):
    """
    Carries an Asset Sale through its stages:
        flow = sale.reach("profit_a", "saved")
    It returns what an earlier test did, or does the missing stages now when the test runs
    on its own. See utils/sale_flow.py.
    """
    from utils.sale_flow import SaleFlow

    return SaleFlow(assets, asset_sale_page, asset_sale_list_page, shared_sale)


@pytest.fixture(scope="session")
def shared_user():
    """The logged-in test user's search text and full name, read once per run. Used by the `current_user` fixture."""
    return {}


@pytest.fixture
def current_user(registration_list_page, shared_user):
    """
    The logged-in test user: {"search_text": the username, "name": the full name as the grids show it}.
    The name is read once from the Created By box of the Asset Registration List, which starts filled
    with "<username>-<Full Name>".
    """
    from playwright.sync_api import expect

    from config.settings import ERP_USERNAME

    if not shared_user:
        registration_list_page.navigate_here()
        expect(registration_list_page.created_by_filter).not_to_have_value("")
        box_text = registration_list_page.read_created_by()
        shared_user["search_text"] = ERP_USERNAME
        shared_user["name"] = box_text.split("-", 1)[1].strip()
    return shared_user

