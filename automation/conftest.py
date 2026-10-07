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


@pytest.fixture
def login_page(page):
    """Login page object, ready to use in any test."""
    from pages.login_page import LoginPage
    return LoginPage(page)


@pytest.fixture
def dashboard_page(page):
    """Dashboard page object (the page shown after login), ready to use."""
    from pages.dashboard_page import DashboardPage
    return DashboardPage(page)


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
    from pages.login_page import LoginPage

    # Open the page at the full size of the maximized browser window.
    context = browser.new_context(no_viewport=True)
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(BASE_URL)

    # Log in once and close the advertisement popup if it appears
    login_page = LoginPage(page)
    login_page.wait_for_login_page()
    login_page.login(TEST_USERNAME, TEST_PASSWORD)
    login_page.close_popup_if_present()

    yield page

    context.tracing.stop()
    context.close()


@pytest.fixture
def finance_dashboard_page(page):
    """Finance (addons) dashboard page object, ready to use."""
    from pages.finance_dashboard_page import FinanceDashboardPage
    return FinanceDashboardPage(page)


@pytest.fixture
def income_statement_page(page):
    """Income Statement report page object, ready to use."""
    from pages.income_statement_page import IncomeStatementPage
    return IncomeStatementPage(page)


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
def shipment_page(assignee_logged_in_page):
    """Asset Shipment page object (the second user's tab), ready to use."""
    from pages.asset_shipment_page import AssetShipmentPage
    return AssetShipmentPage(assignee_logged_in_page)


@pytest.fixture
def challan_page(assignee_logged_in_page):
    """Transfer Challan page object (the Challan tab and popups of a shipment), ready to use."""
    from pages.shipment_challan_page import ShipmentChallanPage
    return ShipmentChallanPage(assignee_logged_in_page)


@pytest.fixture
def challan_approval_page(assignee_logged_in_page):
    """Asset Shipment Challan Approval List page object, ready to use."""
    from pages.shipment_challan_approval_page import ShipmentChallanApprovalPage
    return ShipmentChallanApprovalPage(assignee_logged_in_page)


@pytest.fixture
def in_challan_page(assignee_logged_in_page):
    """Asset Shipment In-Challan page object, ready to use."""
    from pages.shipment_in_challan_page import ShipmentInChallanPage
    return ShipmentInChallanPage(assignee_logged_in_page)


@pytest.fixture
def gate_pass_page(assignee_logged_in_page):
    """Gate Pass Generation page object, ready to use."""
    from pages.gate_pass_page import GatePassPage
    return GatePassPage(assignee_logged_in_page)


@pytest.fixture(scope="session")
def shared_transfer():
    """
    The Asset Shipment flow of this run (shipment, challan, serial, ...), shared
    by every test file so one test can reuse what an earlier test did. Used by
    the `transfer` fixture below; tests do not read it directly.
    """
    return {}


@pytest.fixture
def saved_transfer(
    registrations, shipment_page, challan_page, challan_approval_page, in_challan_page, shared_transfer
):
    """
    Like `transfer`, but the transferred asset is saved in test_data/saved_assets.json
    so a separate run reuses it. See SavedTransferHelper in utils/transfer_helper.py.
    """
    from utils.transfer_helper import SavedTransferHelper

    return SavedTransferHelper(
        registrations, shipment_page, challan_page,
        challan_approval_page, in_challan_page, shared_transfer,
    )


@pytest.fixture
def transfer(
    registrations, shipment_page, challan_page, challan_approval_page, in_challan_page, shared_transfer
):
    """
    Carries one Asset Shipment through its stages:
        flow = transfer.reach("draft_challan")
    It returns what an earlier test did, or does the missing stages now when
    the test runs on its own. See utils/transfer_helper.py.
    """
    from utils.transfer_helper import TransferHelper

    return TransferHelper(
        registrations, shipment_page, challan_page,
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
    registrations, assign_page, unassign_page, internal_movement_page,
    transaction_approval_page, asset_serial_global_list_page,
):
    """
    Gives a test the saved Furniture asset in the state it needs:
        serial = transactions.ensure_assigned()
    It reads the asset's real Assign Status and does only the missing steps.
    See utils/transaction_helper.py.
    """
    from utils.transaction_helper import TransactionHelper

    return TransactionHelper(
        registrations, assign_page, unassign_page, internal_movement_page,
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
    one test can reuse what another created. Used by the `registrations`
    fixture below; tests do not read it directly. The 10 AAQ assets are also
    saved in a file, so a later run reuses them (see utils/saved_registrations.py).
    """
    from utils.saved_registrations import SavedRegistrations

    return SavedRegistrations()


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


@pytest.fixture(scope="module")
def assignee_logged_in_page(browser):
    """
    A second browser tab, logged in as the ASSIGNED employee (the second user
    in .env), shared by every test in one file. The assigned employee is the
    person who acknowledges an assignment, so this tab is separate from the
    main user's tab.
    """
    from config.settings import ASSIGN_USER_PASSWORD, ASSIGN_USER_USERNAME
    from pages.login_page import LoginPage

    # Open the page at the full size of the maximized browser window.
    context = browser.new_context(no_viewport=True)
    tab = context.new_page()
    maximize_window(context, tab)
    tab.goto(BASE_URL)

    login_page = LoginPage(tab)
    login_page.wait_for_login_page()
    login_page.login(ASSIGN_USER_USERNAME, ASSIGN_USER_PASSWORD)
    login_page.close_popup_if_present()

    yield tab

    context.close()


@pytest.fixture
def assignee_screenshot(assignee_logged_in_page, request):
    """
    Numbered screenshots of the assigned employee's tab, like `take_screenshot`
    but for the second user:

        assignee_screenshot("pending list opened")
    """
    def _take(description: str) -> str:
        return take_numbered_screenshot(assignee_logged_in_page, request.node, description)
    return _take


@pytest.fixture
def acknowledgement_page(assignee_logged_in_page):
    """Asset Assign Acknowledgement page object, working in the assigned employee's tab."""
    from pages.asset_assign_acknowledgement_page import AssetAssignAcknowledgementPage
    return AssetAssignAcknowledgementPage(assignee_logged_in_page)


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
def expenses(registrations, expense_page, expense_approval_page, shared_registrations):
    """
    Gives an Asset Expense test the saved Furniture asset and an approved expense:
        serial = expenses.get_serial()
        record = expenses.get_approved_expense("Inventory")
    It returns what an earlier test saved, or makes it when the test runs on
    its own. See utils/expense_helper.py.
    """
    from utils.expense_helper import ExpenseHelper

    return ExpenseHelper(registrations, expense_page, expense_approval_page, shared_registrations)


@pytest.fixture
def voucher_search_page(page):
    """Accounting Voucher Search page object, ready to use."""
    from pages.voucher_search_page import VoucherSearchPage
    return VoucherSearchPage(page)
