"""
HofinAssetFlow: the stages of an asset registration or asset addition that
starts in HOFIN, for the tests in tests/test_32_asset_registration_addition_hofin.py.

The journey has three roles, each with its own login and its own browser
context (a session is never shared between roles):

    HOFIN creator   -> creates and submits the vendor bill      -> Transaction No.
    HOFA acknowledger -> finds that Transaction No. and acknowledges it
    HOFIN approver  -> finds that Transaction No. and approves it

A registration creates a new parent asset. An addition is the same journey with
one parent asset serial chosen in the Fixed Asset Details popup. The values made
by one stage (the Transaction No.) are passed to the next stage by the test, never
saved anywhere else.

How to use it in a test (the `hofin_flow` fixture in conftest.py creates it):

    transaction_no = hofin_flow.create_bill(invoice_no)
    hofin_flow.acknowledge(transaction_no)
    hofin_flow.approve(transaction_no)
"""
from config.settings import (
    HOFA_ACK_PASSWORD,
    HOFA_ACK_USERNAME,
    HOFA_URL,
    HOFIN_APPROVER_PASSWORD,
    HOFIN_APPROVER_USERNAME,
    HOFIN_CREATOR_PASSWORD,
    HOFIN_CREATOR_USERNAME,
    HOFIN_URL,
)
from pages.asset_registration_pending_review_page import AssetRegistrationPendingReviewPage
from pages.asset_serial_global_list_page import AssetSerialGlobalListPage
from pages.hofin_approval_page import HofinApprovalPage
from pages.hofin_login_page import HofinLoginPage
from pages.login_page import LoginPage
from pages.vendor_bill_payable_page import VendorBillPayablePage
from test_data import hofin_asset_data as data
from utils.helpers import unique_name
from utils.logger import action_logger
from utils.run_context import attach_trace_to_report, take_numbered_screenshot, trace_path


class HofinAssetFlow:
    """Runs the HOFIN creator, HOFA acknowledger and HOFIN approver stages."""

    def __init__(self, browser, test_item, maximize_window):
        """
        `browser` is the session browser, `test_item` the running test (it names
        the screenshots and traces) and `maximize_window` the function that
        maximizes a new browser window (from conftest.py).
        """
        self.browser = browser
        self.test_item = test_item
        self.maximize_window = maximize_window
        # Sessions opened by `open_hofa_global_list` as (context, log out method), closed at the end of the test
        self.kept_sessions = []

    # ---- stages ---------------------------------------------------------------

    def create_bill(self, invoice_no: str, parent_serial: str = "") -> str:
        """
        HOFIN creator stage: fill and submit the vendor bill. Without
        `parent_serial` it registers a new asset; with it, it adds to that
        parent asset. Returns the Transaction No. of the bill.
        """
        self.require_logins(HOFIN_CREATOR_USERNAME, HOFIN_CREATOR_PASSWORD, "HOFIN_CREATOR")
        stage = "hofin_creator_addition" if parent_serial != "" else "hofin_creator_registration"
        context, page = self.open_role_page()
        hofin_login = HofinLoginPage(page)
        try:
            hofin_login.open_login_page(HOFIN_URL)
            hofin_login.login(HOFIN_CREATOR_USERNAME, HOFIN_CREATOR_PASSWORD)
            bill = VendorBillPayablePage(page)
            bill.open_create_form()
            bill.fill_bill_header(invoice_no)
            bill.fill_and_add_bill_allocation()
            bill.open_fixed_asset_details()
            bill.fill_fixed_asset_details(parent_serial)
            expected_addition = "YES" if parent_serial != "" else "NO"
            bill.verify_item_row(expected_addition, parent_serial)
            self.take_screenshot(page, "fixed asset details item added")
            bill.confirm_item_details()
            transaction_no = bill.read_transaction_no()
            bill.submit_and_verify()
            self.take_screenshot(page, f"bill {transaction_no} submitted")
        except Exception:
            self.finish_role(context, page, stage, True, hofin_login.log_out)
            raise
        self.finish_role(context, page, stage, False, hofin_login.log_out)
        return transaction_no

    def acknowledge(self, transaction_no: str) -> None:
        """HOFA acknowledger stage: find the Transaction No. in the Pending/Review List and acknowledge it."""
        self.require_logins(HOFA_ACK_USERNAME, HOFA_ACK_PASSWORD, "HOFA_ACK")
        stage = f"hofa_acknowledger_{transaction_no}"
        context, page = self.open_role_page()
        hofa_login = LoginPage(page)
        try:
            self.login_to_hofa(hofa_login, HOFA_ACK_USERNAME, HOFA_ACK_PASSWORD)
            pending_list = AssetRegistrationPendingReviewPage(page)
            pending_list.navigate_here()
            pending_list.search_by_transaction_no(transaction_no)
            pending_list.verify_status(transaction_no, data.STATUS_PENDING)
            self.take_screenshot(page, f"{transaction_no} pending in HOFA")
            pending_list.acknowledge(transaction_no)
            pending_list.search_by_transaction_no(transaction_no)
            pending_list.verify_status(transaction_no, data.STATUS_ACKNOWLEDGED)
            self.take_screenshot(page, f"{transaction_no} acknowledged")
        except Exception:
            self.finish_role(context, page, stage, True, hofa_login.log_out)
            raise
        self.finish_role(context, page, stage, False, hofa_login.log_out)

    def approve(self, transaction_no: str) -> None:
        """HOFIN approver stage: find the Transaction No. in the approval list and approve it."""
        self.require_logins(HOFIN_APPROVER_USERNAME, HOFIN_APPROVER_PASSWORD, "HOFIN_APPROVER")
        stage = f"hofin_approver_{transaction_no}"
        context, page = self.open_role_page()
        hofin_login = HofinLoginPage(page)
        try:
            hofin_login.open_login_page(HOFIN_URL)
            hofin_login.login(HOFIN_APPROVER_USERNAME, HOFIN_APPROVER_PASSWORD)
            approval = HofinApprovalPage(page)
            approval.navigate_here()
            approval.search_by_transaction_no(transaction_no)
            self.take_screenshot(page, f"{transaction_no} waiting for approval")
            approval.approve(transaction_no)
            approval.verify_approved(transaction_no)
            self.take_screenshot(page, f"{transaction_no} approved")
        except Exception:
            self.finish_role(context, page, stage, True, hofin_login.log_out)
            raise
        self.finish_role(context, page, stage, False, hofin_login.log_out)

    def create_parent_asset(self) -> str:
        """
        Register a new parent asset through the three roles (HOFIN creator, HOFA
        acknowledger, HOFIN approver) and return its serial, read from the Global
        List as the newest parent asset.
        """
        registration_no = self.create_bill(unique_name("REG"))
        self.acknowledge(registration_no)
        self.approve(registration_no)
        global_list = self.open_hofa_global_list()
        parent_serial = global_list.read_newest_parent_serial(data.ASSET_ITEM_NAME)
        self.close_all()
        return parent_serial

    def add_extended_asset(self, parent_serial: str) -> None:
        """Add one extended asset to the parent asset through the three roles (the same journey as an addition)."""
        addition_no = self.create_bill(unique_name("ADD"), parent_serial)
        self.acknowledge(addition_no)
        self.approve(addition_no)

    def create_parent_with_extended_asset(self, extension_count: int = 1) -> tuple:
        """
        Register a new parent asset and add `extension_count` extended assets to it.
        Returns (parent serial, [extended serials]): the extended serials are the
        parent serial plus "-1", "-2", ... in the order they were added. Used by the
        tests of other screens that need a parent asset that has extended assets.
        """
        parent_serial = self.create_parent_asset()
        extended_serials = []
        for number in range(1, extension_count + 1):
            self.add_extended_asset(parent_serial)
            extended_serials.append(f"{parent_serial}-{number}")
        return parent_serial, extended_serials

    def open_hofa_global_list(self) -> AssetSerialGlobalListPage:
        """
        Log in to HOFA as the acknowledger and open the Asset Serial Global List.
        The browser stays open, so the test can read from the list; it is closed
        by `close_all` when the test ends.
        """
        self.require_logins(HOFA_ACK_USERNAME, HOFA_ACK_PASSWORD, "HOFA_ACK")
        context, page = self.open_role_page()
        hofa_login = LoginPage(page)
        self.kept_sessions.append((context, hofa_login.log_out))
        self.login_to_hofa(hofa_login, HOFA_ACK_USERNAME, HOFA_ACK_PASSWORD)
        global_list = AssetSerialGlobalListPage(page)
        global_list.navigate_here()
        return global_list

    def close_all(self) -> None:
        """Log out and close the browser windows kept open for the test. Called by the fixture at the end of the test."""
        for context, log_out in self.kept_sessions:
            self.try_log_out(log_out)
            context.close()
        self.kept_sessions = []

    # ---- helpers ----------------------------------------------------------------

    def login_to_hofa(self, login_page, username: str, password: str) -> None:
        """Open HOFA, sign in with the ERP sign-in screen (`login_page`) and close the advertisement popup."""
        action_logger.info(f"Open URL: {HOFA_URL}")
        login_page.page.goto(HOFA_URL)
        login_page.wait_for_login_page()
        login_page.login(username, password)
        login_page.close_popup_if_present()

    def open_role_page(self) -> tuple:
        """Open a new browser window (its own context) and start recording a trace. Returns (context, page)."""
        context = self.browser.new_context(no_viewport=True)
        context.tracing.start(screenshots=True, snapshots=True)
        page = context.new_page()
        self.maximize_window(context, page)
        return context, page

    def finish_role(self, context, page, stage: str, failed: bool, log_out) -> None:
        """
        Log the role out and close its browser window. `log_out` is the log-out
        method of the role's login page. Logging out leaves the account with no open
        session, so the next stage or test can log in with it without ending
        another session. A failed stage first takes a screenshot and saves its
        trace in the report; a passed stage drops the trace.
        """
        if failed:
            self.take_screenshot(page, f"{stage} FAILED")
        self.try_log_out(log_out)
        if failed:
            trace_file = trace_path(f"{self.test_item.name}_{stage}")
            context.tracing.stop(path=trace_file)
            attach_trace_to_report(trace_file)
        else:
            context.tracing.stop()
        context.close()

    def try_log_out(self, log_out) -> None:
        """
        Call a log-out method. A log-out that does not complete is only logged: it
        must never hide the result of the stage that has just run.
        """
        try:
            log_out()
        except Exception as error:
            action_logger.info(f"The log out did not complete: {error}")

    def take_screenshot(self, page, description: str) -> None:
        """Take the next numbered screenshot of the test."""
        take_numbered_screenshot(page, self.test_item, description)

    def require_logins(self, username, password, env_prefix: str) -> None:
        """Stop with a clear message when a login of the flow is missing in .env."""
        assert username and password, (
            f"The login for {env_prefix} is missing. Add {env_prefix}_USERNAME and "
            f"{env_prefix}_PASSWORD to .env (see .env.example)."
        )
