"""
SingleChallanListPage: what the four Single Challan screens have in common
(Fixed Asset > Single Challan): Asset Single Out Challan, Asset Single Out
Challan Approval List, Asset Single In-Challan and Gate Pass Generation.

All four show the same filters and the same grid (`#challanListTable`), and a
challan is opened from its Out Challan Number link in the same popup
(`#singleChallanDetailsModal`). Each screen has a small class that inherits this
one and adds what it does (create, approve, acknowledge, gate pass).
See `automation/element_catalog/asset_single_out_challan.md`.
"""
from playwright.sync_api import expect

from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Position of the Out Challan Number cell in a result row (0-based)
OUT_CHALLAN_COLUMN_INDEX = 3

# Read-only fields of the challan popup: (name shown in results, element id)
POPUP_FIELDS = [
    ("Out Challan No", "#challanNumberDetails"),
    ("In Challan No", "#inChallanNumberDetails"),
    ("From Project", "#fromProjectDetails"),
    ("To Project", "#toProjectDetails"),
    ("Status", "#transactionStatusType"),
    ("From Branch", "#fromBranchDetails"),
    ("To Branch", "#toBranchDetails"),
    ("Created By", "#challanCreatedByDetails"),
]

# Maximum time to wait for a popup or the loading overlay (milliseconds)
POPUP_TIMEOUT = 15000


class SingleChallanListPage(BasePage):
    """Filters, grid and challan popup shared by the Single Challan screens."""

    # Set by each subclass: the text of the Single Challan menu link
    MENU_LINK = ""

    def __init__(self, page):
        super().__init__(page)
        # Out Challan Number filter (free text)
        self.out_challan_filter = page.locator("#outChallanNumber")
        # Challan Status filter: PENDING, APPROVED, REJECTED, ACKNOWLEDGED, SENDBACK
        self.status_filter = page.locator("#assetChallanStatus")
        # Runs the filter
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid and the line under it, e.g. "Showing 1 to 10 of 359 entries"
        self.grid = page.locator("#challanListTable")
        self.entries_info = page.locator("#challanListTable_info")
        # Challan popup opened from an Out Challan Number link
        self.popup = page.locator("#singleChallanDetailsModal")
        self.popup_close_button = self.popup.get_by_role("button", name="Close", exact=True)

    def navigate_here(self) -> None:
        """Open this screen via the Single Challan menu."""
        self.open_single_challan_submenu(self.MENU_LINK)
        self.wait_until_visible(self.search_button, "Search button")

    def search(self) -> None:
        """Click Search and wait until the grid shows the result."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_to_reload(self.entries_info)

    def filter_by_out_challan_no(self, out_challan_no: str) -> None:
        """Type an Out Challan Number into its filter and run the search."""
        self.type_text(self.out_challan_filter, out_challan_no, "Out Challan Number filter")
        self.search()

    def filter_by_status(self, status: str) -> None:
        """Choose a Challan Status (for example 'PENDING') and run the search."""
        action_logger.info(f"Filter: Challan Status -> {status}")
        self.status_filter.select_option(label=status)
        self.search()

    # ---- reading the grid -------------------------------------------------

    def read_headers(self) -> list:
        """Return the grid's column headings, in order."""
        headers = []
        for text in self.grid.locator("thead th").all_inner_texts():
            headers.append(text.strip())
        return headers

    def _row_for(self, out_challan_no: str):
        """Return the grid row (locator) that contains this Out Challan Number."""
        return self.grid.locator("tbody tr", has_text=out_challan_no).first

    def read_row(self, out_challan_no: str) -> dict:
        """
        Return the grid row of this Out Challan Number as a dict: column
        heading -> cell text, e.g. row["Status"]. Waits for the row to be shown.
        """
        row = self._row_for(out_challan_no)
        self.wait_until_visible(row, f"grid row of {out_challan_no}")
        headers = self.read_headers()
        cells = row.locator("td").all_inner_texts()
        result = {}
        for index in range(len(headers)):
            if index < len(cells):
                result[headers[index]] = cells[index].strip()
        return result

    def get_newest_out_challan_no(self) -> str:
        """Return the Out Challan Number in the first (newest) row of the grid."""
        first_row = self.grid.locator("tbody tr").first
        self.wait_until_visible(first_row, "first grid row")
        return first_row.locator("td").nth(OUT_CHALLAN_COLUMN_INDEX).inner_text().strip()

    def row_has_preview_link(self, out_challan_no: str) -> bool:
        """Return True if the last cell (Preview) of this challan's row holds a link."""
        row = self._row_for(out_challan_no)
        self.wait_until_visible(row, f"grid row of {out_challan_no}")
        return row.locator("td").last.locator("a").count() > 0

    def row_has_edit_link(self, out_challan_no: str) -> bool:
        """Return True if this challan's row has an Edit link (only a Draft has one)."""
        row = self._row_for(out_challan_no)
        self.wait_until_visible(row, f"grid row of {out_challan_no}")
        return row.get_by_role("link", name="Edit", exact=True).count() > 0

    # ---- the challan popup ------------------------------------------------

    def open_popup(self, out_challan_no: str) -> None:
        """Click the Out Challan Number link to open the challan popup."""
        link = self.grid.get_by_role("link", name=out_challan_no, exact=True)
        self.click(link, f"Out Challan Number {out_challan_no} link")
        self.wait_until_visible(self.popup, "Challan popup")

    def read_popup_values(self) -> dict:
        """Return the read-only fields of the open popup as a dict: field name -> text (empty field gives "")."""
        values = {}
        for field_name, selector in POPUP_FIELDS:
            field = self.popup.locator(selector)
            values[field_name] = field.input_value().strip()
        return values

    def close_popup(self) -> None:
        """Close the challan popup."""
        self.click(self.popup_close_button, "Challan popup Close button")
        expect(self.popup).to_be_hidden(timeout=POPUP_TIMEOUT)

    def close_popup_if_open(self) -> None:
        """Close the challan popup when it is still open (it may already have closed after an action)."""
        if self.popup.is_visible():
            self.close_popup()

    # ---- checks: each one says what was expected and what was found --------

    def verify_row_status(self, out_challan_no: str, expected_status: str) -> None:
        """Confirm the grid row of this Out Challan Number shows `expected_status` in Status."""
        found = self.read_row(out_challan_no).get("Status", "")
        assertion_logger.info(f"Verifying challan {out_challan_no} has status {expected_status}")
        if found != expected_status:
            raise AssertionError(
                f"Expected challan {out_challan_no} to have status '{expected_status}' but found '{found}'."
            )

    def verify_popup_values(self, expected: dict) -> None:
        """Confirm the open popup shows every value in `expected` ({field name: text}); names each difference."""
        found = self.read_popup_values()
        assertion_logger.info("Verifying the challan popup values")
        problems = []
        for name, wanted in expected.items():
            if found.get(name) != wanted:
                problems.append(f"{name}: expected '{wanted}' but found '{found.get(name)}'")
        assert not problems, f"The challan popup is not as expected: {problems}"
