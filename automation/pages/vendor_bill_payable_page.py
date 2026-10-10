"""
VendorBillPayablePage: HOFIN > Vendor > Payable Journal > "+ Create" (the
"Create Vendor Bill Payable" form) and its "Fixed Asset Details" popup.

This is the screen the HOFIN creator uses to start an asset registration or an
asset addition. The form is always filled with the values in
`test_data/hofin_asset_data.py`; only the values that must differ on every run
(the bill number, and for an addition the parent asset serial) are passed in.
See `automation/element_catalog/vendor_bill_payable.md` for every field.

Registration and addition share every step except two inside the popup: for an
addition the "Fixed Asset Addition" box is ticked and the parent asset serial is
chosen. That is the `parent_serial` argument of `fill_fixed_asset_details`.
"""
import re

from pages.base_page import BasePage
from test_data import hofin_asset_data as data
from utils.logger import action_logger, assertion_logger

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Most months the Bill Date calendar is moved back to reach the business date
MAX_MONTHS_BACK = 24

# Times Add is clicked in the Fixed Asset Details popup, and the time to wait for the item row after each click (milliseconds)
ADD_ITEM_ATTEMPTS = 3
ITEM_ROW_WAIT = 20000

# Maximum time to wait for the bill to be saved, the Transaction No. to appear
# and the screen to change after Submit (milliseconds)
SAVE_TIMEOUT = 60000


class VendorBillPayablePage(BasePage):
    """Page object for the Create Vendor Bill Payable form and its Fixed Asset Details popup."""

    def __init__(self, page):
        super().__init__(page)
        # Menu: Vendor, its Payable Journal link, and the "+ Create" link
        self.vendor_menu = page.get_by_role("link", name="Vendor")
        self.payable_journal_link = page.locator('a[href="/brac/vendor/pending-bill-payable-list"]')
        self.create_link = page.get_by_role("link", name="+ Create")

        # Header of the form
        self.transaction_no_field = page.locator("#transactionNo")
        # Read-only Date field: it holds the business date
        self.date_field = page.locator("#transactionDate")
        self.vendor_input = page.locator("#vendor input")
        self.purchase_method_input = page.locator("#purchaseMethod input")
        self.bill_invoice_no_field = page.get_by_role("textbox", name="Bill/Invoice No.: *")
        # Read-only box that opens a calendar
        self.bill_date_field = page.locator("#billDate")
        self.total_bill_amount_field = page.get_by_role("textbox", name="Total Bill Amount: *")
        self.bank_account_input = page.locator("#bankAccount input")

        # Calendar of the Bill Date: month and year buttons, back arrow, day cells
        self.calendar_titles = page.locator("bs-datepicker-navigation-view button.current")
        self.calendar_back_button = page.locator("bs-datepicker-navigation-view button.previous")
        self.calendar_days = page.locator('bs-days-calendar-view td[role="gridcell"]:not(.is-other-month) span')

        # Bill Allocation Details
        self.project_input = page.locator("#project input")
        self.ac_code_input = page.locator("#chartOfAccount input")
        self.purpose_input = page.locator("#purpose input")
        self.allocation_amount_field = page.get_by_role("textbox", name="Amount: *", exact=True)
        # The first "Add" after the Bill Allocation Details heading (the Advance
        # Adjustment section above it has its own Add button)
        self.allocation_add_button = page.locator("text=Bill Allocation Details").locator(
            'xpath=following::*[normalize-space(text())="Add"][1]'
        )

        # Link that opens the Fixed Asset Details popup (shown after the allocation is added)
        self.fixed_asset_details_link = page.get_by_text("Fixed Asset Details", exact=True)

        # Fixed Asset Details popup
        self.popup = page.locator("app-vendor-fixed-asset-modal")
        self.popup_bill_allocation_input = self.popup.locator("#budgetAllocation input")
        # Tick box "Fixed Asset Addition"
        self.addition_checkbox = self.popup.locator("#isFixedAssetAddition")
        # Search box for the parent asset, shown after the box above is ticked
        self.parent_serial_input = self.popup.locator("#fixedAssetProfile input")
        self.parent_serial_selected = self.popup.locator("#fixedAssetProfile .ng-value-label")
        self.source_of_fund_input = self.popup.locator("#sourceOfFund input")
        self.quantity_field = self.popup.locator("#quantity")
        self.unit_price_field = self.popup.locator("#unitPrice")
        self.asset_item_input = self.popup.locator("#assetItemName input")
        self.item_specification_field = self.popup.get_by_placeholder("Eg. XYZ-4523453")
        # Adds the item to the list inside the popup
        self.popup_add_button = self.popup.locator("a.btn-add")
        # The row of the added item (the list also has a "Total" row, shown before any item is added)
        self.popup_item_row = self.popup.locator("table tbody tr", has_text=data.ASSET_ITEM_NAME).first

        # Buttons of the form
        self.confirm_button = page.get_by_role("button", name="Confirm")
        self.yes_button = page.get_by_role("button", name="Yes")
        self.submit_button = page.get_by_text("Submit", exact=True)

    # ---- open the form --------------------------------------------------------

    def open_create_form(self) -> None:
        """Click Vendor > Payable Journal > + Create and wait for the empty form."""
        self.click(self.vendor_menu, "Vendor menu")
        self.click(self.payable_journal_link, "Payable Journal link")
        self.click(self.create_link, "+ Create link")
        self.wait_for_page_load()
        self.wait_until_visible(self.date_field, "Date field")

    # ---- bill header -------------------------------------------------------------

    def fill_bill_header(self, invoice_no: str) -> None:
        """
        Fill the top part of the form: Vendor, Purchase Method, Bill/Invoice No.,
        Bill Date (the business date shown in the Date field), Total Bill Amount
        and Bank Account.
        """
        self.choose_from_ng_select(self.vendor_input, data.VENDOR_SEARCH_TEXT, data.VENDOR_OPTION)
        self.choose_from_ng_select(self.purchase_method_input, "", data.PURCHASE_METHOD_OPTION)
        self.type_with_keys(self.bill_invoice_no_field, invoice_no, "Bill/Invoice No. field")
        self.pick_bill_date_from_date_field()
        self.type_with_keys(self.total_bill_amount_field, data.BILL_AMOUNT, "Total Bill Amount field")
        self.choose_from_ng_select(
            self.bank_account_input, data.BANK_ACCOUNT_SEARCH_TEXT, data.BANK_ACCOUNT_OPTION
        )

    def pick_bill_date_from_date_field(self) -> None:
        """
        Set the Bill Date to the date shown in the read-only Date field (the
        business date). The calendar opens on the current month, so it is moved
        back until it shows the month and year of that date, then the day is
        clicked.
        """
        date_text = self.get_date_field_value()
        day, month, year = date_text.split("-")
        month_name = MONTH_NAMES[int(month) - 1]
        self.click(self.bill_date_field, "Bill Date field")
        self.wait_until_visible(self.calendar_titles.first, "Bill Date calendar")
        for _ in range(MAX_MONTHS_BACK):
            shown_month = self.calendar_titles.first.inner_text().strip()
            shown_year = self.calendar_titles.nth(1).inner_text().strip()
            if shown_month == month_name and shown_year == year:
                break
            self.click(self.calendar_back_button, "Calendar back arrow")
        day_cell = self.calendar_days.filter(has_text=re.compile(f"^{int(day)}$")).first
        self.click(day_cell, f"Calendar day {int(day)}")
        assert self.bill_date_field.input_value() == date_text, (
            f"The Bill Date should be the business date {date_text} but shows "
            f"'{self.bill_date_field.input_value()}'."
        )

    def get_date_field_value(self) -> str:
        """Return the business date shown in the read-only Date field, e.g. '13-09-2026'."""
        return self.date_field.input_value().strip()

    # ---- bill allocation -----------------------------------------------------------

    def fill_and_add_bill_allocation(self) -> None:
        """
        Fill Bill Allocation Details (Project, A/C Code, Purpose, Amount) and
        click Add. The bill is saved by this click: the Transaction No. appears
        and the "Fixed Asset Details" link is shown.
        """
        self.choose_from_ng_select(self.project_input, data.PROJECT_SEARCH_TEXT, data.PROJECT_OPTION)
        # The A/C Code list is filled only after a project is chosen
        self.choose_from_ng_select(self.ac_code_input, data.AC_CODE_SEARCH_TEXT, data.AC_CODE_OPTION)
        self.choose_from_ng_select(self.purpose_input, data.PURPOSE_SEARCH_TEXT, data.PURPOSE_OPTION)
        self.type_with_keys(self.allocation_amount_field, data.BILL_AMOUNT, "Bill Allocation Amount field")
        self.click(self.allocation_add_button, "Add button of Bill Allocation Details")
        self.wait_for_page_load()
        self.wait_until_visible(self.fixed_asset_details_link, "Fixed Asset Details link")

    # ---- fixed asset details popup ---------------------------------------------------

    def open_fixed_asset_details(self) -> None:
        """Click the "Fixed Asset Details" link and wait for the popup."""
        self.click(self.fixed_asset_details_link, "Fixed Asset Details link")
        self.wait_until_visible(self.popup_bill_allocation_input, "Bill Allocation box of the popup")

    def fill_fixed_asset_details(self, parent_serial: str = "") -> None:
        """
        Fill the Fixed Asset Details popup and add the item to its list.

        With no `parent_serial` this is an asset registration. With a
        `parent_serial` it is an asset addition: the "Fixed Asset Addition" box
        is ticked and that parent asset is chosen. The Bill Allocation must be
        chosen first, because it narrows the list of parent assets.
        """
        self.click(self.popup_bill_allocation_input, "Bill Allocation box of the popup")
        self.click(self.page.get_by_role("option").first, "the only Bill Allocation option")
        if parent_serial != "":
            self.choose_parent_asset(parent_serial)
        self.click(self.source_of_fund_input, "Source Of Fund box")
        self.click(self.page.get_by_role("option").first, "first Source Of Fund option")
        self.type_with_keys(self.quantity_field, data.QUANTITY, "Quantity field")
        self.type_with_keys(self.unit_price_field, data.UNIT_PRICE, "Unit Price field")
        self.choose_from_ng_select(self.asset_item_input, data.ASSET_ITEM_SEARCH_TEXT, data.ASSET_ITEM_OPTION)
        self.type_with_keys(self.item_specification_field, data.ITEM_SPECIFICATION, "Item Specification field")
        self.add_item_to_popup_list()

    def add_item_to_popup_list(self) -> None:
        """
        Click Add in the popup until the item shows in the popup's item list. The
        list is empty until the item is added, so clicking again never adds it twice.
        """
        for attempt in range(ADD_ITEM_ATTEMPTS):
            self.click(self.popup_add_button, "Add button of the popup")
            if self.is_shown_within(self.popup_item_row, "item row in the popup", ITEM_ROW_WAIT):
                return
        raise AssertionError(
            f"The item was not added to the list of the Fixed Asset Details popup after {ADD_ITEM_ATTEMPTS} clicks on Add."
        )

    def choose_parent_asset(self, parent_serial: str) -> None:
        """
        Tick "Fixed Asset Addition", search the parent asset serial and choose
        it. Only parent assets are listed, so the search shows exactly one option.
        """
        self.addition_checkbox.check()
        self.click(self.parent_serial_input, "Fixed Asset Serial No box")
        # The search runs on the server: wait for the answer to the full serial
        with self.page.expect_response(f"**listForFixedAssetProfile**search={parent_serial}&**"):
            self.parent_serial_input.press_sequentially(parent_serial)
        option = self.page.get_by_role("option", name=parent_serial, exact=True)
        self.click(option, f"parent asset option {parent_serial}")
        shown = self.parent_serial_selected.inner_text().strip()
        assert shown == parent_serial, (
            f"The parent asset {parent_serial} was chosen but the box shows '{shown}'."
        )

    def verify_item_row(self, expected_addition: str, parent_serial: str = "") -> None:
        """
        Confirm the first row of the popup's item list: its "FAA" column reads
        `expected_addition` ("YES" for an addition, "NO" for a registration)
        and, for an addition, the parent asset serial is shown in the row.
        """
        assertion_logger.info("Verifying the item row of the Fixed Asset Details popup")
        cells = [c.strip() for c in self.popup_item_row.locator("td").all_inner_texts()]
        assert expected_addition in cells, (
            f"The item row should show FAA = {expected_addition} but its cells are {cells}."
        )
        if parent_serial != "":
            assert parent_serial in cells, (
                f"The item row should show the parent asset {parent_serial} but its cells are {cells}."
            )

    def confirm_item_details(self) -> None:
        """Click Confirm, then Yes on the "Do you want to continue?" question."""
        self.click(self.confirm_button, "Confirm button")
        self.wait_until_visible(self.yes_button, "Yes button")
        self.click(self.yes_button, "Yes button")

    # ---- transaction number and submit --------------------------------------------------

    def read_transaction_no(self) -> str:
        """
        Return the Transaction No. of the bill (it starts with VP). Waits until
        the box has a value, because the number is filled in a moment after the
        bill is saved.
        """
        self.page.wait_for_function(
            "document.querySelector('#transactionNo') && document.querySelector('#transactionNo').value !== ''",
            timeout=SAVE_TIMEOUT,
        )
        transaction_no = self.transaction_no_field.input_value().strip()
        action_logger.info(f"Transaction No. of the bill: {transaction_no}")
        return transaction_no

    def submit_and_verify(self) -> None:
        """
        Click Submit and confirm the bill was submitted: the screen changes to
        the read-only view of the bill.
        """
        self.click(self.submit_button, "Submit button")
        assertion_logger.info("Verifying the bill was submitted")
        try:
            self.page.wait_for_url("**/vendor-bill-payable/view/**", timeout=SAVE_TIMEOUT)
        except Exception:
            raise AssertionError(
                "After Submit the bill should open in view mode but the page shows "
                f"{self.page.url}."
            )
        self.wait_for_page_load()
