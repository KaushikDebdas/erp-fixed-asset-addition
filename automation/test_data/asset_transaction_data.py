"""
asset_transaction_data.py: fixed values used by the Asset Transaction tests
(Asset Assign, Asset Un Assign, Asset Internal Movement and their lists).
"""

# Transaction types as the Transaction List and Approval List name them
ASSIGN = "ASSIGN"
UNASSIGN = "UNASSIGN"
TRANSFER = "TRANSFER"  # the list's name for an Internal Movement

# Employee the asset is assigned to (typed in the Employee PIN Search box)
ASSIGNEE_PIN = "00015370"
ASSIGNEE_NAME = "Sachindra Nath Ghosh"

# Employee the asset is handed over to on Un Assign. The hand-over person
# must be a different employee from the current holder.
HANDOVER_SEARCH = "130276"
HANDOVER_PIN = "00130276"
HANDOVER_NAME = "Md. Abubokkor Siddik"

# The branch the test user is logged in to (shown, disabled, in Branch Name)
USER_BRANCH = "Head Office [ BDHO ]"

# The building the asset is moved to on Internal Movement
MOVE_BUILDING = "Head Office"

# Note typed on the assignment that the `assigned_asset` fixture creates
SETUP_ASSIGN_NOTE = "AUTOMATION_TEST setup assignment"

# Message shown when the assigned employee acknowledges an assignment
from test_data.toast_messages import ACKNOWLEDGE_TOAST  # noqa: F401 (also imported from here by the smoke suite)

# Notes typed on the transactions the helper (utils/transaction_helper.py) makes
# to bring the saved asset into the state a test needs
SETUP_UNASSIGN_NOTE = "AUTOMATION_TEST setup unassignment"
SETUP_MOVE_NOTE = "AUTOMATION_TEST setup movement"

# Every note typed by these tests starts with this text
NOTE_PREFIX = "AUTOMATION_TEST"

# The two values of an asset's Assign Status
ASSIGNED = "ASSIGNED"
UNASSIGNED = "UNASSIGNED"

# What the three transaction forms show for the saved Furniture asset
# (field id on the form -> text)
FURNITURE_FORM_DETAILS = {
    "assetName": "Cabinet Table",
    "subCategoryName": "Wooden Furniture",
    "categoryName": "Furniture",
    "groupName": "Furniture and Fixture",
    "projectName": "Microfinance (Dabi)",
}

# The auto-filled fields of the forms; none of them can be typed in
FORM_READ_ONLY_FIELDS = [
    "assetName",
    "subCategoryName",
    "categoryName",
    "groupName",
    "projectName",
    "previousAssignStatus",
]


def build_form_expectation(profile: dict) -> dict:
    """
    Return what a transaction form must show for an asset, taken from the
    asset's Asset Serial Global List row (see AssetSerialGlobalListPage.get_row_values).

    Example:
        expected = build_form_expectation(profile)
        # {"assetName": "Cabinet Table", ..., "previousAssignStatus": "UNASSIGNED"}
    """
    return {
        "assetName": profile["item_name"],
        "subCategoryName": profile["sub_category"],
        "categoryName": profile["category"],
        "groupName": profile["group"],
        "previousAssignStatus": profile["assign_status"],
    }
