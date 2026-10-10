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
import importlib.util
import os
import sys

import pytest
from playwright.sync_api import sync_playwright
from config.settings import BASE_URL, ENVIRONMENT
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
    Also stops the run at once when a selected test reads a voucher PDF (it uses
    the `voucher_search_page` fixture) and this Python does not have `pypdf`.
    Tests that do not read PDFs, such as the Generate Barcode tests, run anyway.
    """
    TEST_COUNT["total"] = len(session.items)
    if session.config.option.collectonly:
        return
    voucher_tests = [item for item in session.items if "voucher_search_page" in item.fixturenames]
    if voucher_tests and importlib.util.find_spec("pypdf") is None:
        pytest.exit(
            f"pypdf is not installed in this Python ({sys.executable}), and {len(voucher_tests)} selected "
            "tests read voucher PDFs. Run the tests with the project's own Python, from the project folder: "
            "python -m pytest automation (after activating this project's .venv), "
            "or .venv/Scripts/python.exe -m pytest automation",
            returncode=2,
        )


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
    from config.settings import TEST_PASSWORD, TEST_USERNAME

    context, page = open_logged_in_tab(browser, TEST_USERNAME, TEST_PASSWORD)

    yield page

    log_out_quietly(page)
    context.tracing.stop()
    context.close()


@pytest.fixture(scope="module")
def assign_user_logged_in_page(browser, request):
    """
    Like `logged_in_page`, but the tab is logged in as the Asset Assign user
    (ASSIGN_USER_USERNAME / ASSIGN_USER_PASSWORD in .env). Use it in a test file
    that runs the Asset Assign screens with that user, by overriding `page` to
    return this tab (see tests/test_33_asset_assign_extended_assets.py).
    """
    from config.settings import ASSIGN_USER_PASSWORD, ASSIGN_USER_USERNAME

    assert ASSIGN_USER_USERNAME and ASSIGN_USER_PASSWORD, (
        "The Asset Assign user is missing. Add ASSIGN_USER_USERNAME and ASSIGN_USER_PASSWORD to .env."
    )
    context, page = open_logged_in_tab(browser, ASSIGN_USER_USERNAME, ASSIGN_USER_PASSWORD)

    yield page

    log_out_quietly(page)
    context.tracing.stop()
    context.close()


def log_out_quietly(page) -> None:
    """
    Log the user of this tab out, so the account has no session left open when a test
    file ends (the ERP allows one session per user). A log-out that does not complete
    is only logged: it must not turn a passed test file into an error.
    """
    from pages.login_page import LoginPage
    from utils.logger import action_logger

    try:
        LoginPage(page).log_out()
    except Exception as error:
        action_logger.info(f"The log out at the end of the test file did not complete: {error}")


def open_logged_in_tab(browser, username: str, password: str) -> tuple:
    """
    Open a new browser window on HOFA (the Fixed Asset application), log in with
    the given user and close the advertisement popup if it appears. Tracing is
    started. Returns (context, page).
    """
    from pages.login_page import LoginPage

    # Open the page at the full size of the maximized browser window.
    context = browser.new_context(no_viewport=True)
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(BASE_URL)

    login_page = LoginPage(page)
    login_page.wait_for_login_page()
    login_page.login(username, password)
    login_page.close_popup_if_present()
    return context, page


@pytest.fixture
def hofin_flow(browser, request):
    """
    The stages of an asset registration / addition that starts in HOFIN (HOFIN
    creator, HOFA acknowledger, HOFIN approver), each in its own browser window.
    Needed because that journey logs in to two applications with three users, so
    it cannot use the single `page` fixture. See utils/hofin_flow.py.
    """
    from utils.hofin_flow import HofinAssetFlow

    flow = HofinAssetFlow(browser, request.node, maximize_window)
    yield flow
    flow.close_all()


@pytest.fixture(scope="session")
def hofin_flow_data():
    """
    An empty dictionary shared by all the tests of a run, so a test can leave a value
    (the parent and extended asset serials) for the next test, in any file, that needs it.
    """
    return {}


@pytest.fixture
def parent_with_extended(hofin_flow, hofin_flow_data):
    """
    A parent asset that has one extended asset, as {"parent": serial, "extended": serial}.
    Made through HOFIN, HOFA and HOFIN the first time a test asks for it in a run (a few
    minutes); every later test of the run gets the same two assets.
    """
    if "extended_serial" not in hofin_flow_data:
        parent_serial, extended_serials = hofin_flow.create_parent_with_extended_asset()
        hofin_flow_data["parent_serial"] = parent_serial
        hofin_flow_data["extended_serial"] = extended_serials[0]
    return {"parent": hofin_flow_data["parent_serial"], "extended": hofin_flow_data["extended_serial"]}


@pytest.fixture
def parent_with_inactive_extended(
    hofin_flow, hofin_flow_data, asset_serial_global_list_page, asset_write_off_page,
    asset_write_off_list_page, asset_write_off_approval_list_page
):
    """
    A second parent asset with three extended assets, the last one written off
    (disposed, so inactive), as {"parent": serial, "active": [two serials],
    "inactive": serial}. Made once per run: through HOFIN, HOFA and HOFIN, then the
    third extended asset is set to DAMAGE, written off and approved. It is a
    different parent from `parent_with_extended`, so a test that assigns it does
    not disturb the other tests.
    """
    from test_data.hofin_asset_data import WRITE_OFF_PROJECT
    from utils.asset_flow import write_off_and_approve

    if "inactive_pair" not in hofin_flow_data:
        parent_serial, extended_serials = hofin_flow.create_parent_with_extended_asset(3)
        write_off_and_approve(
            asset_serial_global_list_page, asset_write_off_page, asset_write_off_list_page,
            asset_write_off_approval_list_page, extended_serials[2], WRITE_OFF_PROJECT,
        )
        hofin_flow_data["inactive_pair"] = {
            "parent": parent_serial, "active": extended_serials[:2], "inactive": extended_serials[2],
        }
    return hofin_flow_data["inactive_pair"]


@pytest.fixture
def assigned_parent_with_extended(
    parent_with_extended, assign_page, transaction_approval_page, asset_serial_global_list_page, acknowledgement_page
):
    """
    The parent asset and its extended asset, ASSIGNED to the test employee and
    acknowledged, which is the state Asset Internal Movement and Asset Un Assign
    need (an asset with an acknowledgement pending is not offered there). It does
    only the steps that are missing: assigns and approves when the parent is
    UNASSIGNED, then acknowledges when an acknowledgement is waiting. Works in the
    tab of the user that is the assigned employee. Returns the same dictionary
    as `parent_with_extended`.
    """
    from test_data.asset_transaction_data import ASSIGNEE_PIN, UNASSIGNED
    from test_data.toast_messages import ACKNOWLEDGE_TOAST
    from utils.asset_flow import assign_and_approve

    parent_serial = parent_with_extended["parent"]
    status = asset_serial_global_list_page.open_and_read_assign_status(parent_serial)
    if status == UNASSIGNED:
        assign_and_approve(
            assign_page, transaction_approval_page, parent_serial, ASSIGNEE_PIN, "AUTOMATION_TEST setup assign"
        )
    acknowledgement_page.navigate_here()
    if acknowledgement_page.has_pending_for_serial(parent_serial):
        acknowledgement_page.open_details_of_row_with_serial(parent_serial)
        toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
        acknowledgement_page.verify_toast_contains(toast, ACKNOWLEDGE_TOAST, "Acknowledge in the setup")
    return parent_with_extended


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
def acknowledgement_page(page):
    """Asset Assign Acknowledgement page object. The assigned employee is the logged-in user, so it works in the main tab."""
    from pages.asset_assign_acknowledgement_page import AssetAssignAcknowledgementPage
    return AssetAssignAcknowledgementPage(page)


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

    from config.settings import TEST_USERNAME

    if not shared_user:
        registration_list_page.navigate_here()
        expect(registration_list_page.created_by_filter).not_to_have_value("")
        box_text = registration_list_page.read_created_by()
        shared_user["search_text"] = TEST_USERNAME
        shared_user["name"] = box_text.split("-", 1)[1].strip()
    return shared_user

