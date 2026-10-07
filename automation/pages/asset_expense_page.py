"""
AssetExpensePage: Fixed Asset > Asset Expenditure > Asset Expense screen.

The screen opens as a list of expenses (filter by Status, Search, results
grid). The **Create** link opens the "Create Asset Expense" popup, and
clicking an Expense ID in the list opens the same popup with the saved
values. See `automation/element_catalog/asset_expense.md`.

Things the screen needs, in this order (verified on staging):
    1. the asset serial (typing it opens the suggestion; there is no search button)
    2. the expense amount of the asset and **Add** (this fills the total)
    3. only then the Expense Source, because the Credit A/C is loaded when the
       source is chosen and needs the asset in the grid
    4. Inventory: Category, Sub Category and Item Name; Accounts: these three
       are disabled
    5. the Debit A/C, the vendor (required for both sources) and the Expense Ref.
"""
import re

from pages.base_page import OPEN_LIST_ATTEMPTS, BasePage
from utils.logger import action_logger


class AssetExpensePage(BasePage):
    """Page object for the Asset Expense list and its Create/Edit popup."""

    def __init__(self, page):
        super().__init__(page)
        # The list behind the popup
        self.status_filter = page.locator("select#status")
        self.search_button = page.get_by_role("button", name="Search")
        self.create_link = page.locator("[onclick='resetAssetExpenseForm()']", has_text="Create").locator("visible=true").first
        self.results_table = page.locator("#editExpenseTable")
        # The "Create Asset Expense" popup
        self.popup = page.locator(".modal.in")
        self.popup_close_button = self.popup.get_by_role("button", name="Close").first
        self.asset_serial_box = page.locator("#assetSerialId")
        self.suggestions = page.locator("ul.ui-autocomplete li:visible")
        self.amount_for_asset_field = page.locator("#expenseAmountIndividual")
        self.add_button = page.locator("#btn-add")
        self.asset_grid = page.locator("#assetDetailsTable")
        self.expense_source_select = page.locator("select#expenseSource")
        self.category_select = page.locator("select#expenseCategory")
        self.sub_category_select = page.locator("select#expenseSubCategory")
        self.item_select = page.locator("select#itemName")
        self.debit_account_select = page.locator("select#debitAccount")
        self.credit_account_select = page.locator("select#creditAccount")
        self.total_amount_field = page.locator("#expenseAmount")
        self.vendor_link = self.popup.get_by_role("link", name="-Select Party-")
        self.vendor_search_box = page.locator("input.select2-input[type=text]:visible")
        self.expense_ref_field = page.locator("#expenseRef")
        self.remarks_field = page.locator("#remarks")
        self.draft_button = page.locator("#draftExpense")
        self.submit_button = page.locator("#createExpense")

    # ---- the list --------------------------------------------------------------

    def navigate_here(self) -> None:
        """Open the Asset Expense list via the Asset Expenditure menu."""
        self.open_asset_expenditure_submenu("Asset Expense")
        self.wait_until_visible(self.search_button, "Search button")

    def search(self, status: str = None) -> None:
        """Pick a Status (when given), click Search and wait for the grid."""
        if status:
            action_logger.info(f"Filter: Status -> {status}")
            self.status_filter.select_option(status)
        self.click(self.search_button, "Search button")
        self.wait_for_table_to_reload(self.results_table)

    def get_status_options(self) -> list:
        """Return every value of the Status filter, placeholder first."""
        return self.status_filter.evaluate("s => Array.from(s.options).map(o => o.text.trim())")

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_expense_id_by_ref(self, expense_ref: str) -> str:
        """
        Return the Expense ID of the row whose Expense Ref. is `expense_ref`
        (the reference is random, so it finds this test's own expense).
        """
        self.wait_for_row_or_no_data(self.results_table, expense_ref)
        row = self.results_table.locator("tbody tr", has_text=expense_ref)
        assert row.count() > 0, f"No expense with Expense Ref. {expense_ref} was found in the list."
        expense_id = row.first.locator("td").nth(2).inner_text().strip()
        action_logger.info(f"Expense ID generated: {expense_id} (Expense Ref. {expense_ref})")
        return expense_id

    def get_row_status(self, expense_id: str) -> str:
        """Return the Status shown in the row of this Expense ID (the cell that holds a status word)."""
        row = self.results_table.locator("tbody tr", has_text=expense_id).first
        status_cell = row.locator("td", has_text=re.compile(r"^(DRAFT|PENDING|APPROVED|REJECTED|SENDBACK)$")).first
        return status_cell.inner_text().strip()

    # ---- opening the popup -----------------------------------------------------

    def open_create_form(self) -> None:
        """Click Create and wait for the Create Asset Expense popup."""
        self.click(self.create_link, "Create link")
        self.wait_until_visible(self.asset_serial_box, "Asset Serial box")

    def open_expense(self, expense_id: str) -> None:
        """Click the Expense ID of a row to open it with its saved values."""
        row = self.results_table.locator("tbody tr", has_text=expense_id).first
        self.click(row.get_by_role("link", name=expense_id), f"Expense ID {expense_id} link")
        self.wait_until_visible(self.expense_ref_field, "Expense Ref. field")
        self.page.wait_for_function(
            "document.querySelector('#expenseRef') && document.querySelector('#expenseRef').value !== ''"
        )

    def wait_for_saved_selections(self, uses_item_chain: bool) -> None:
        """
        Wait until the drop-downs of an opened expense have loaded their saved
        choices (they fill in a moment after the rest of the popup). With the
        Inventory source Sub Category and Item Name are saved too.
        """
        selects = ["debitAccount", "creditAccount"]
        if uses_item_chain:
            selects += ["expenseCategory", "expenseSubCategory", "itemName"]
        condition = " && ".join(
            f"document.querySelector('#{s}') && document.querySelector('#{s}').selectedIndex > 0" for s in selects
        )
        self.page.wait_for_function(condition)

    def close_popup(self) -> None:
        """Close the popup without saving."""
        self.click(self.popup_close_button, "Close button of the expense popup")
        self.popup.wait_for(state="hidden")

    # ---- filling the form ----------------------------------------------------------

    def select_asset_by_serial(self, serial: str) -> None:
        """Type the serial and click the suggestion; the read-only asset fields fill in."""
        suggestion = self.suggestions.filter(has_text=serial).first
        # Type the serial key by key until the suggestion list shows it
        for attempt in range(OPEN_LIST_ATTEMPTS):
            action_logger.info("Type into: Asset Serial box")
            self.asset_serial_box.fill("")
            self.asset_serial_box.press_sequentially(serial, delay=40)
            if self.is_shown_within(suggestion, f"Suggestion for {serial}"):
                break
        self.wait_until_visible(suggestion, f"Suggestion for {serial}")
        self.click(suggestion, f"Suggestion for {serial}")
        self.page.wait_for_function(
            "document.querySelector('#assetName') && document.querySelector('#assetName').value !== ''"
        )

    def get_value(self, field_id: str) -> str:
        """Return the text of an input or text area in the popup, e.g. 'assetName'."""
        action_logger.info(f"Read value of: {field_id}")
        return self.popup.locator(f"#{field_id}").input_value().strip()

    def get_selected_text(self, select_id: str) -> str:
        """Return the visible text of the option chosen in a drop-down, e.g. 'creditAccount'."""
        action_logger.info(f"Read selected option of: {select_id}")
        return self.page.locator(f"select#{select_id}").evaluate(
            "s => (s.options[s.selectedIndex] || {}).text || ''"
        ).strip()

    def enter_amount_and_add_asset(self, amount: str) -> None:
        """Type the expense amount of the asset and click Add; the asset joins the grid and the total fills in."""
        self.type_text(self.amount_for_asset_field, amount, "Expense Amount field")
        self.click(self.add_button, "Add button")
        real_row = self.asset_grid.locator("tbody tr").filter(has_not_text="No data available")
        self.wait_until_visible(real_row.first, "asset grid row")
        self.page.wait_for_function(
            "document.querySelector('#expenseAmount') && document.querySelector('#expenseAmount').value !== ''"
        )

    def get_asset_grid_serials(self) -> list:
        """Return the Asset Serial of every row in the asset grid (second visible cell)."""
        rows = self.asset_grid.locator("tbody tr").filter(has_not_text="No data available")
        return [rows.nth(i).locator("td:visible").nth(1).inner_text().strip() for i in range(rows.count())]

    def get_total_expense_amount(self) -> str:
        """Return the Total Expense Amount, e.g. '5000'."""
        return self.total_amount_field.input_value().strip()

    def choose_expense_source(self, source: str) -> None:
        """Choose Inventory or Accounts; the Credit A/C is filled in by the screen."""
        action_logger.info(f"Select: Expense Source -> {source}")
        self.expense_source_select.select_option(label=source)
        self.page.wait_for_function("document.querySelector('#creditAccount').selectedIndex > 0")

    def get_credit_account(self) -> str:
        """Return the Credit A/C the screen chose."""
        return self.get_selected_text("creditAccount")

    def is_category_chain_enabled(self) -> bool:
        """Return True if Category, Sub Category and Item Name can be chosen (Inventory only)."""
        return self.category_select.is_enabled()

    def select_category_sub_category_and_item(self, category: str, sub_category: str, item: str) -> None:
        """Choose Category, then Sub Category, then Item Name (each list loads after the one before)."""
        action_logger.info(f"Select: Category -> {category}, Sub Category -> {sub_category}, Item -> {item}")
        self.category_select.select_option(label=category)
        self.page.wait_for_function("document.querySelectorAll('#expenseSubCategory option').length > 1")
        self.sub_category_select.select_option(label=sub_category)
        self.page.wait_for_function("document.querySelectorAll('#itemName option').length > 1")
        self.item_select.select_option(label=item)

    def select_debit_account(self, account: str) -> None:
        """Choose the Debit A/C by its full name, e.g. 'Other Maintenance Expenses[5108010101-07]'."""
        action_logger.info(f"Select: Debit A/C -> {account}")
        self.debit_account_select.select_option(label=account)

    def select_vendor(self, search_text: str, option_name: str) -> None:
        """Pick the Vendor/Supplier/Lessor Name through its search list (same widget as on the registration form)."""
        self.click(self.vendor_link, "Vendor/Supplier/Lessor Name link")
        self.type_text(self.vendor_search_box, search_text, "Vendor search box")
        option = self.page.get_by_role("option", name=option_name)
        self.wait_until_visible(option, f"Vendor option '{option_name}'")
        self.click(option, f"Vendor option '{option_name}'")

    def is_vendor_shown(self, vendor_name: str) -> bool:
        """Return True if the popup shows this vendor as chosen."""
        return self.popup.locator(".select2-chosen", has_text=vendor_name).count() > 0

    def enter_expense_ref(self, expense_ref: str) -> None:
        """Type the Expense Ref."""
        self.type_text(self.expense_ref_field, expense_ref, "Expense Ref. field")

    def enter_remarks(self, remarks: str) -> None:
        """Type the Remarks/Note."""
        self.type_text(self.remarks_field, remarks, "Remarks/Note field")

    def get_date_of_entry(self) -> str:
        """Return the Date of Entry (the business date), dd/mm/yyyy."""
        return self.get_value("dateOfEntry")

    # ---- saving --------------------------------------------------------------------

    def draft_and_get_toast(self) -> str:
        """Click Draft, return the message shown, and wait for the popup to close (when it saved)."""
        self.wait_for_toast_to_clear()
        self.click(self.draft_button, "Draft button")
        return self.get_toast_text()

    def submit_and_get_toast(self) -> str:
        """Click Submit, return the message shown."""
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        return self.get_toast_text()

    def wait_for_popup_to_close(self) -> None:
        """Wait until the popup has closed after a successful save."""
        self.popup.wait_for(state="hidden")
