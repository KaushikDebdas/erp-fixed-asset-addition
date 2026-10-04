"""
GatePassPage: Fixed Asset > Asset Transfer > Gate Pass Generation screen.

Lists acknowledged challans with a Preview link that opens the gate pass as a
PDF in a new browser tab. Used by the Asset Shipment end-to-end flow
(projects/fixedasset/e2e-flows/asset-transfer-shipment.md, step 26).
Locators come from automation/element_catalog/asset_gate_pass_generation.md.
"""
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Name of the menu link under Fixed Asset > Asset Transfer (the Single Challan
# menu has a link with the same name; this class uses the Asset Transfer one)
MENU_LINK_NAME = "Gate Pass Generation"

# Part of the PDF address that identifies the gate pass report
REPORT_URL_PART = "generateAssetGatePassReport"


class GatePassPage(BasePage):
    """Page object for the Gate Pass Generation screen."""

    def __init__(self, page):
        super().__init__(page)
        # Out Challan No filter (free text)
        self.out_challan_filter = page.locator("#outChallanNo")
        # Runs the filter
        self.search_button = page.get_by_role("button", name=" Search")
        # Results grid and the line under it, e.g. "Showing 1 to 1 of 1 entries"
        self.grid = page.locator("#challanListTable")
        self.entries_info = page.locator("#challanListTable_info")

    def navigate_here(self) -> None:
        """Open Gate Pass Generation via the Asset Transfer menu."""
        self.open_asset_transfer_submenu(MENU_LINK_NAME)
        self.wait_until_visible(self.search_button, "Search button")

    def search(self) -> None:
        """Click Search and wait until the grid shows the result."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_to_reload(self.entries_info)

    def filter_by_out_challan_no(self, out_challan_no: str) -> None:
        """Type an Out Challan No into its filter and run the search."""
        self.type_text(self.out_challan_filter, out_challan_no, "Out Challan No filter")
        self.search()

    def read_headers(self) -> list:
        """Return the grid's column headings, in order."""
        headers = []
        for text in self.grid.locator("thead th").all_inner_texts():
            headers.append(text.strip())
        return headers

    def _row_for(self, out_challan_no: str):
        """Return the grid row (locator) that contains this Out Challan No."""
        return self.grid.locator("tbody tr", has_text=out_challan_no).first

    def read_row(self, out_challan_no: str) -> dict:
        """
        Return the grid row of this Out Challan No as a dict: column heading ->
        cell text, e.g. row["Status"]. Waits for the row to be shown.
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

    def read_preview(self, out_challan_no: str) -> dict:
        """
        Click Preview for this Out Challan No. The gate pass opens as a PDF in
        a new tab, which has no page text. So the tab's address is taken, the
        tab is closed, and the same address is fetched with the logged-in
        session. Returns {"url", "status", "content_type", "size"}.
        """
        row = self._row_for(out_challan_no)
        self.wait_until_visible(row, f"grid row of {out_challan_no}")
        preview_link = row.locator("td").last.locator("a")
        with self.page.context.expect_page() as new_tab_info:
            self.click(preview_link, f"Preview of {out_challan_no}")
        preview_tab = new_tab_info.value
        preview_tab.wait_for_load_state("load")
        preview_url = preview_tab.url
        preview_tab.close()
        response = self.page.context.request.get(preview_url)
        preview = {
            "url": preview_url,
            "status": response.status,
            "content_type": response.headers.get("content-type", ""),
            "size": len(response.body()),
        }
        action_logger.info(f"Gate pass preview read for {out_challan_no}: status {preview['status']}")
        return preview

    # ------------------------------------------------------------------
    # Checks: each one raises AssertionError saying what was expected and found
    # ------------------------------------------------------------------

    def verify_preview_is_pdf(self, preview: dict, out_challan_id: str) -> None:
        """
        Confirm the preview returned by read_preview is the gate pass PDF: the
        address contains 'generateAssetGatePassReport', the status is 200 and
        the content type contains 'pdf'. `out_challan_id` is the challan id
        (e.g. '594'); it is only named in the failure text.
        """
        assertion_logger.info(f"Verifying the gate pass preview of challan {out_challan_id} is a PDF")
        if REPORT_URL_PART not in preview["url"]:
            raise AssertionError(
                f"Expected the preview address of challan {out_challan_id} to contain "
                f"'{REPORT_URL_PART}' but found '{preview['url']}'."
            )
        if preview["status"] != 200:
            raise AssertionError(
                f"Expected status 200 for the gate pass of challan {out_challan_id} but found {preview['status']}."
            )
        if "pdf" not in preview["content_type"]:
            raise AssertionError(
                f"Expected a PDF content type for the gate pass of challan {out_challan_id} "
                f"but found '{preview['content_type']}'."
            )
