"""
asset_split_data.py: the values the Asset Serial Split tests type and expect.

The asset that is split is the saved Land asset (see utils/split_helper.py).
Its measurement and value come from build_land_asset_data() in
test_data/asset_registration_data.py (measurement 12.5, unit price 25000).
"""

# What the split form is filled with
SPLIT_INTO = "2"
SPLIT_REMARKS = "AUTOMATION_TEST split note"
FIRST_LINE_PERCENTAGE = "50"

# How the Land asset is shown on the split form and in the split popups
LAND_ITEM_NAME = "Land"
LAND_MEASUREMENT_TEXT = "12.50"
LAND_VALUE_TEXT = "25000.00"
LAND_ACC_DEPRECIATION_TEXT = "0.00"

# The same values as numbers, for the split result lines
LAND_MEASUREMENT = 12.5
LAND_VALUE = 25000.0

# The user who creates and approves the splits (shown in the Created By / Approved By columns)
# Column headings of the Split List and Split Approval List grids
SPLIT_GRID_COLUMNS = [
    "SL", "Asset Split No.", "Asset Group", "Project Name", "Department Name",
    "Asset Serial No.", "Split Into", "Remarks", "Created By", "Status",
    "Approved By", "Approval Date",
]
