"""
AssetSplitViewPopup: the read-only "Asset Split View" popup that opens when an
Asset Split No. link is clicked on the Asset Serial Split List and the Asset
Serial Split Approval List. Both pages use this one class, so the popup's
locators live in a single place. See `automation/element_catalog/asset_serial_split_list.md`.
"""
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Heading of the popup
POPUP_TITLE = "Asset Split View"


class AssetSplitViewPopup(BasePage):
    """Page object for the Asset Split View popup."""

    def __init__(self, page):
        super().__init__(page)
        # The open popup (the page also holds closed copies of it)
        self.popup = page.locator(".modal.in")
        # Split Into box, the first thing that shows once the popup is open
        self.split_into_field = self.popup.locator("#splitInto")
        # Close button
        self.close_button = self.popup.get_by_role("button", name="Close").first
        # One row per split line
        self.split_lines = self.popup.locator("#assetSerialSplitList tbody tr")

    def wait_until_open(self) -> None:
        """Wait until the popup is open and its fields are shown."""
        self.wait_until_visible(self.split_into_field, "Split Into field of the popup")

    def get_value(self, field_id: str) -> str:
        """Return the value of a read-only field in the popup, e.g. 'assetSerial'."""
        action_logger.info(f"Read value of popup field: {field_id}")
        return self.popup.locator(f"#{field_id}").first.input_value().strip()

    def get_title(self) -> str:
        """Return the popup's heading."""
        return self.popup.locator("h4, .modal-title").first.inner_text().strip()

    def verify_shows(self, expected: dict, line_count: int) -> None:
        """
        Confirm the popup has the right heading, shows every field value in
        `expected` ({field id: text}) and lists `line_count` split lines.
        """
        assertion_logger.info("Verifying the Asset Split View popup")
        problems = []
        if self.get_title() != POPUP_TITLE:
            problems.append(f"title: expected '{POPUP_TITLE}' but found '{self.get_title()}'")
        for field_id, wanted in expected.items():
            found = self.get_value(field_id)
            if found != wanted:
                problems.append(f"{field_id}: expected '{wanted}' but found '{found}'")
        found_lines = self.split_lines.count()
        if found_lines != line_count:
            problems.append(f"split lines: expected {line_count} but found {found_lines}")
        assert not problems, f"The Asset Split View popup is not as expected: {problems}"

    def close(self) -> None:
        """Close the popup and wait until it is gone."""
        self.click(self.close_button, "Close button of Asset Split View popup")
        self.popup.first.wait_for(state="hidden")
