"""
VoucherSearchPage: Accounting > Voucher > Voucher Search screen.

Used to find the voucher that an approved transaction created, by its
Transaction Number (for an Asset Expense this is the Expense ID), and to read
the voucher that Preview opens as a PDF in a new tab. See
`automation/element_catalog/voucher_search.md`.
"""
import re

from pages.base_page import OPEN_LIST_ATTEMPTS, BasePage
from utils.helpers import day_of_month
from utils.logger import action_logger, assertion_logger
from utils.voucher_pdf import parse_voucher, read_voucher_text


class VoucherSearchPage(BasePage):
    """Page object for the Voucher Search screen."""

    def __init__(self, page):
        super().__init__(page)
        self.from_date_field = page.locator("#fromDate")
        self.to_date_field = page.locator("#toDate")
        self.calendar_icons = page.locator("[class*=date-image-contr]:visible")
        self.voucher_type_select = page.locator("select#voucherType")
        self.module_select = page.locator("select#module")
        self.transaction_no_field = page.locator("#transactionNo")
        self.search_button = page.get_by_role("button", name="Search")
        self.results_table = page.locator("#tableVouchers")

    def navigate_here(self) -> None:
        """
        Open Voucher Search in the Accounting module. The Accounting tab of
        the top bar opens the module in the same browser tab.
        """
        # Start from another module so Voucher Search is built fresh every time
        self.open_fixed_asset_module()
        accounting_tab = self.page.get_by_text("Accounting", exact=True).first
        self.click(accounting_tab, "Accounting tab")
        self.page.wait_for_url("**/accounting**")
        self.wait_for_page_load()
        voucher_menu = self.page.get_by_text("Voucher", exact=True).first
        self.click(voucher_menu, "Voucher menu")
        link = self.page.get_by_role("link", name="Voucher Search", exact=True)
        self.wait_until_visible(link, "Voucher Search menu link")
        self.click(link, "Voucher Search menu link")
        self.wait_for_page_load()
        self.wait_until_visible(self.search_button, "Search button")
        # The calendars need the page scripts: wait until their icons are shown
        self.calendar_icons.first.wait_for(state="visible")

    def get_accounting_date(self) -> str:
        """Return the accounting (business) date shown in the page header, dd/mm/yyyy."""
        header_text = self.page.locator("body").inner_text()
        match = re.search(r"Accounting Date\s*:\s*(\d{2})-(\d{2})-(\d{4})", header_text)
        assert match, "The accounting date was not found in the page header."
        return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"

    def set_date_range(self, date_text: str) -> None:
        """
        Put the same date in Date From and Date To through the calendars. The
        calendar opens on the business month, so clicking the day number is
        enough (`date_text` is dd/mm/yyyy).
        """
        day = day_of_month(date_text)
        for index, name in [(0, "Date From"), (1, "Date To")]:
            day_cell = self.page.get_by_role("cell", name=day, exact=True).last
            for attempt in range(OPEN_LIST_ATTEMPTS):
                self.click(self.calendar_icons.nth(index), f"{name} calendar icon")
                if self.is_shown_within(day_cell, f"{name} calendar", timeout=5000):
                    break
            self.wait_until_visible(day_cell, f"{name} calendar day {day}")
            self.click(day_cell, f"{name} calendar day {day}")
            # Let this calendar close before the next one is opened
            self.page.wait_for_function(
                "Array.from(document.querySelectorAll('.datepicker-dropdown')).every(e => e.offsetParent === null)"
            )

    def get_voucher_type_options(self) -> list:
        """Return every value of the Voucher Type filter, placeholder first."""
        return self.voucher_type_select.evaluate("s => Array.from(s.options).map(o => o.text.trim())")

    def get_module_options(self) -> list:
        """Return every value of the Module filter, placeholder first."""
        return self.module_select.evaluate("s => Array.from(s.options).map(o => o.text.trim())")

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def choose_module(self, module: str) -> None:
        """Pick a Module in the filter (does not search yet)."""
        action_logger.info(f"Filter: Module -> {module}")
        self.module_select.select_option(label=module)

    def search_by_transaction_no(self, transaction_no: str) -> None:
        """
        Type the Transaction Number with real key presses (it must match
        exactly), click Search, and wait for the result or the empty message.
        """
        self.transaction_no_field.click()
        self.transaction_no_field.fill("")
        self.transaction_no_field.press_sequentially(transaction_no, delay=40)
        self.click(self.search_button, "Search button")
        self.wait_for_row_or_no_data(self.results_table, transaction_no)

    def search_without_transaction_no(self) -> None:
        """Click Search with the other filters as set and wait for the grid."""
        self.click(self.search_button, "Search button")
        self.results_table.locator("tbody tr").first.wait_for(state="visible")

    def is_voucher_listed(self, transaction_no: str) -> bool:
        """Return True if a result row has this Transaction No."""
        return self.results_table.locator("tbody tr", has_text=transaction_no).count() > 0

    def get_row_values(self, transaction_no: str) -> dict:
        """Return the Date, Voucher No., Transaction No, Amount, Particular and Status of a row."""
        row = self.results_table.locator("tbody tr", has_text=transaction_no).first
        cells = [c.strip() for c in row.locator("td:visible").all_inner_texts()]
        return {
            "date": cells[0],
            "voucher_number": cells[1],
            "transaction_no": cells[2],
            "amount": cells[3],
            "particular": cells[4],
            "status": cells[5],
        }

    def read_voucher_preview(self, transaction_no: str) -> dict:
        """
        Click Preview for this Transaction No. The voucher opens as a PDF in a
        new tab, which has no page text. So the tab's address is taken, the tab
        is closed, and the same address is fetched with the logged-in session
        and read with `pypdf`. Returns the parsed voucher (see
        `utils/voucher_pdf.parse_voucher`) plus `url` and `pdf_status`.
        """
        row = self.results_table.locator("tbody tr", has_text=transaction_no).first
        with self.page.context.expect_page() as new_tab_info:
            self.click(row.locator("td").last.locator("a"), f"Preview of {transaction_no}")
        preview_tab = new_tab_info.value
        preview_tab.wait_for_load_state("load")
        preview_url = preview_tab.url
        preview_tab.close()
        response = self.page.context.request.get(preview_url)
        text = read_voucher_text(response.body())
        voucher = parse_voucher(text)
        voucher["text"] = text
        voucher["url"] = preview_url
        voucher["pdf_status"] = response.status
        voucher["content_type"] = response.headers.get("content-type", "")
        action_logger.info(f"Voucher preview read for {transaction_no}: voucher {voucher['voucher_number']}")
        return voucher

    def verify_registration_voucher(self, registration_number: str, expected: dict) -> None:
        """
        Confirm the voucher of an approved asset registration (see
        test_data.asset_registration_data.build_registration_voucher for
        `expected`). The search row is found by the Registration Number, and
        the Preview PDF must be this registration's voucher: same voucher
        number as the row, "Reference no: <Registration Number>" printed on it,
        the expected date, project, branch, accounts and amounts. Fails and
        names everything that was different.
        """
        assert self.is_voucher_listed(registration_number), (
            f"No voucher was found for Registration Number {registration_number}."
        )
        row = self.get_row_values(registration_number)
        voucher = self.read_voucher_preview(registration_number)
        assertion_logger.info(f"Verifying the voucher of registration {registration_number}")

        problems = []
        particular_pattern = (
            rf"{re.escape(expected['particular_group'])}\[\d+\] Registered by AAQ\. "
            rf"Asset Item: {re.escape(expected['item_name'])}"
        )
        # The search row shows the date without a leading zero, e.g. 20/9/2026
        expected_row_date = "/".join(str(int(part)) for part in expected["date"].split("/"))
        checks = [
            ("search row date", row["date"], expected_row_date),
            ("search row amount", row["amount"], expected["amount_in_search"]),
            ("search row status", row["status"], "Approved"),
            ("PDF status code", voucher["pdf_status"], 200),
            ("voucher title", voucher["title"], "JOURNAL VOUCHER"),
            ("voucher number (PDF and search row)", voucher["voucher_number"], row["voucher_number"]),
            ("creation date", voucher["creation_date"], expected["date"]),
            ("posted date", voucher["posted_date"], expected["date"]),
            ("project", voucher["project"], expected["project"]),
            ("total debit", voucher["total_debit"], expected["amount_on_voucher"]),
            ("total credit", voucher["total_credit"], expected["amount_on_voucher"]),
        ]
        for name, found, wanted in checks:
            if found != wanted:
                problems.append(f"{name}: expected '{wanted}' but found '{found}'")
        if not re.fullmatch(particular_pattern, row["particular"]):
            problems.append(f"search row particular: '{row['particular']}' does not match '{particular_pattern}'")
        if expected["branch"] not in (voucher["branch"] or ""):
            problems.append(f"branch: expected '{expected['branch']}' in '{voucher['branch']}'")
        if "pdf" not in voucher["content_type"]:
            problems.append(f"content type: expected a PDF but found '{voucher['content_type']}'")

        # The two account lines: the asset account is debited and the credit account is credited
        wanted_lines = [
            {**expected["debit"], "debit": expected["amount_on_voucher"], "credit": "0.00"},
            {**expected["credit"], "debit": "0.00", "credit": expected["amount_on_voucher"]},
        ]
        if voucher["lines"] != wanted_lines:
            problems.append(f"account lines: expected {wanted_lines} but found {voucher['lines']}")

        # The voucher belongs to this registration: its number is printed as the reference
        flat_text = " ".join(voucher["text"].split())
        if f"Reference no: {registration_number}" not in flat_text:
            problems.append(f"the voucher text does not show 'Reference no: {registration_number}'")

        assert not problems, f"The voucher of registration {registration_number} is not as expected: {problems}"

    def verify_no_voucher(self, transaction_no: str) -> None:
        """Confirm the search for this Transaction No found no voucher. Fails with the row that was found."""
        assertion_logger.info(f"Verifying no voucher exists for {transaction_no}")
        if self.is_voucher_listed(transaction_no):
            row = self.get_row_values(transaction_no)
            raise AssertionError(f"Expected no voucher for {transaction_no} but found one: {row}")
