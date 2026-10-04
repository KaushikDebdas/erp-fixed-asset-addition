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


def pytest_configure(config):
    """
    Runs once at session start. Points Allure's output at this run's
    dated folder instead of a fixed top-level allure-results/ directory.
    """
    run_dir = get_run_dir()
    config.option.allure_report_dir = str(run_dir / "allure-results")
    write_environment_info(BASE_URL, ENVIRONMENT)


def pytest_runtest_logstart(nodeid, location):
    """Writes a START line to the log when a test begins, so the log shows where each test starts."""
    test_logger.info(f"========== START: {nodeid.split('::')[-1]} ==========")


def pytest_runtest_logreport(report):
    """
    Writes an END line to the log when a test finishes, with its result and
    how long it took. A test that could not even start (set-up error) is
    reported as ERROR.
    """
    test_finished = report.when == "call"
    test_could_not_start = report.when == "setup" and report.failed
    if not (test_finished or test_could_not_start):
        return

    test_name = report.nodeid.split("::")[-1]
    if test_could_not_start:
        result = "ERROR (set-up failed)"
    elif report.skipped:
        result = "SKIPPED"
    else:
        result = "FAILED" if report.failed else "PASSED"
    test_logger.info(f"========== END: {test_name} - {result} in {report.duration:.1f} seconds ==========")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Runs once at the end of the session: builds the single-file HTML report."""
    generate_html_report()


@pytest.fixture(scope="session")
def browser():
    """
    One browser instance shared across the whole test session.

    - headless=False: the browser window is VISIBLE, so you can watch the test.
    - --start-maximized: the window opens at the full size of whatever screen
      this code runs on (laptop, big monitor, ...).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        yield browser
        browser.close()


def maximize_window(context, page) -> None:
    """
    Maximize the browser window that holds `page`, so every screen opens at
    the full size of the monitor. Each new browser context opens its own
    window, so this runs for every tab we create (Chromium only).
    """
    cdp_session = context.new_cdp_session(page)
    window = cdp_session.send("Browser.getWindowForTarget")
    cdp_session.send(
        "Browser.setWindowBounds",
        {"windowId": window["windowId"], "bounds": {"windowState": "maximized"}},
    )
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


@pytest.fixture(scope="session")
def profile_assets(browser):
    """
    Two freshly approved assets shared by every Asset Profile test file, so
    the whole run creates them only once:
        "land":  a Land asset with Measurement 12.5 (unit Decimal), splittable
        "plain": a Cabinet Table asset with no measurement, not splittable
    Each value is {"registration_number": ..., "serial": ...}.
    They are created in their own browser tab, which logs in on its own.
    """
    from config.settings import TEST_PASSWORD, TEST_USERNAME
    from pages.asset_registration_aaq_page import AssetRegistrationAaqPage
    from pages.asset_registration_approval_list_page import AssetRegistrationApprovalListPage
    from pages.asset_registration_list_page import AssetRegistrationListPage
    from pages.login_page import LoginPage
    from test_data.asset_registration_data import build_land_asset_data, build_registration_data
    from utils.asset_flow import create_approved_asset

    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    maximize_window(context, page)
    page.goto(BASE_URL)

    login_page = LoginPage(page)
    login_page.wait_for_login_page()
    login_page.login(TEST_USERNAME, TEST_PASSWORD)
    login_page.close_popup_if_present()

    aaq_page = AssetRegistrationAaqPage(page)
    registration_list_page = AssetRegistrationListPage(page)
    approval_list_page = AssetRegistrationApprovalListPage(page)

    assets = {
        "land": create_approved_asset(
            aaq_page, registration_list_page, approval_list_page, build_land_asset_data()
        ),
        "plain": create_approved_asset(
            aaq_page, registration_list_page, approval_list_page, build_registration_data()
        ),
    }
    context.close()
    return assets


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
    fixture below; tests do not read it directly.
    """
    return {}


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


def _create_asset_in_tab(tab):
    """Register, submit and approve one plain asset in the given tab; return its details."""
    from pages.asset_registration_aaq_page import AssetRegistrationAaqPage
    from pages.asset_registration_approval_list_page import AssetRegistrationApprovalListPage
    from pages.asset_registration_list_page import AssetRegistrationListPage
    from test_data.asset_registration_data import build_registration_data
    from utils.asset_flow import create_approved_asset

    return create_approved_asset(
        AssetRegistrationAaqPage(tab),
        AssetRegistrationListPage(tab),
        AssetRegistrationApprovalListPage(tab),
        build_registration_data(),
    )


@pytest.fixture(scope="module")
def unassigned_asset(logged_in_page):
    """
    A freshly approved asset that is not assigned to anyone, for the tests of
    one file. Returns {"registration_number": ..., "serial": ...}.
    """
    return _create_asset_in_tab(logged_in_page)


@pytest.fixture(scope="module")
def assigned_asset(logged_in_page):
    """
    A freshly approved asset that is already assigned to the test employee, for
    the tests of one file. Returns {"registration_number": ..., "serial": ...}.
    """
    from pages.asset_assign_page import AssetAssignPage
    from pages.transaction_approval_list_page import TransactionApprovalListPage
    from test_data.asset_transaction_data import ASSIGNEE_PIN, SETUP_ASSIGN_NOTE
    from utils.asset_flow import assign_and_approve

    asset = _create_asset_in_tab(logged_in_page)
    assign_and_approve(
        AssetAssignPage(logged_in_page),
        TransactionApprovalListPage(logged_in_page),
        asset["serial"],
        ASSIGNEE_PIN,
        SETUP_ASSIGN_NOTE,
    )
    return asset


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
def voucher_search_page(page):
    """Accounting Voucher Search page object, ready to use."""
    from pages.voucher_search_page import VoucherSearchPage
    return VoucherSearchPage(page)
