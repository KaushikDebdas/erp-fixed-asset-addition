"""
Test data for the asset registration / asset addition flow that starts in HOFIN
(HOFIN creator -> HOFA acknowledger -> HOFIN approver).

Every value was read from the live QA screens (see
`automation/element_catalog/vendor_bill_payable.md`). If QA data changes, change
the value here, in this one file.
"""
from config.settings import HOFA_ACK_USERNAME
from utils.helpers import employee_pin_from_username

# --- The HOFA user of the HOFIN-asset tests ------------------------------------
# The HOFA acknowledger also works the HOFA screens of the HOFIN-asset tests
# (test_32, test_33) and is the employee the assets are assigned to and who
# acknowledges them. Its login name is its employee PIN without the leading zeros.
HOFA_ACK_EMPLOYEE_PIN = employee_pin_from_username(HOFA_ACK_USERNAME)

# --- Vendor bill header ------------------------------------------------------
# Text typed to open the vendor list, and the option chosen from it
VENDOR_SEARCH_TEXT = "SU0006"
VENDOR_OPTION = "SU000634 -3DEVs"
PURCHASE_METHOD_OPTION = "Direct Purchase Method (DPM)"
# Text typed to open the bank account list, and the option chosen from it
BANK_ACCOUNT_SEARCH_TEXT = "Gulshan"
BANK_ACCOUNT_OPTION = "1501200901911006-Gulshan-BRAC Bank PLC"

# --- Bill allocation ---------------------------------------------------------
PROJECT_SEARCH_TEXT = "015"
PROJECT_OPTION = "015-Microfinance (Dabi)"
AC_CODE_SEARCH_TEXT = "Furn"
AC_CODE_OPTION = "1202010501-01-Furniture and Fixture"
PURPOSE_SEARCH_TEXT = "Furniture"
PURPOSE_OPTION = "Capex Payment-Furniture & Fixture"
# A fixed asset A/C code is accepted only when the amount is 20000 or more
BILL_AMOUNT = "25000"

# --- Fixed Asset Details popup -----------------------------------------------
ASSET_ITEM_SEARCH_TEXT = "Sofa"
ASSET_ITEM_OPTION = "171798695282-Sofa Set"
# The item name as it is shown in the Asset Serial Global List
ASSET_ITEM_NAME = "Sofa Set"
QUANTITY = "1"
UNIT_PRICE = "25000"
# Start of the Item Specification. utils/hofin_assets.py adds the date and time to it,
# so every asset it registers can be found again by its own Item Specification.
ITEM_SPECIFICATION = "AUTO-SPEC"

# The project as the Asset Write-off screen lists it
WRITE_OFF_PROJECT = "[015] Microfinance (Dabi)"

# --- HOFIN approval list -----------------------------------------------------
APPROVAL_FEATURE_SEARCH_TEXT = "bill"
APPROVAL_FEATURE_OPTION = "Vendor Bill Payable-Vendor"

# --- Messages and statuses ---------------------------------------------------
ACKNOWLEDGED_TOAST = "Asset registration acknowledged successfully."
STATUS_PENDING = "PENDING"
STATUS_ACKNOWLEDGED = "ACKNOWLEDGED"
STATUS_APPROVED = "APPROVED"
# Serial of an asset added to a parent is the parent serial plus "-1", "-2", ...
FIRST_EXTENSION_SUFFIX = "-1"
# Number of extended assets the data-preparation test adds to its new parent asset
DATA_PREP_EXTENDED_COUNT = 1
# Number of extended assets of the parent asset the Global List tests use
# (test_32): the parent "<serial>" with "<serial>-1" and "<serial>-2"
GLOBAL_LIST_EXTENDED_COUNT = 2

# --- What the HOFA Asset Serial Global List shows for a HOFIN asset (Sofa Set) ---
# Read on env42 on 2026-11-04 (CR FAHOV2-643 F01S01, F01S02)
PROFILE_ROW = {
    "item_name": "Sofa Set",
    "sub_category": "Furniture",
    "category": "Furniture",
    "group": "Furniture and Fixture",
    "project_in_grid": "[015] Microfinance (Dabi)",
    "assign_status": "UNASSIGNED",
    "utilization_status": "IN_USE",
}
# Popup fields of a new HOFIN asset ({field id: text}). The price is UNIT_PRICE with two decimals.
PROFILE_POPUP = {
    "assetName": "Sofa Set",
    "subCategory": "Furniture",
    "category": "Furniture",
    "group": "Furniture and Fixture",
    "projectName": "Microfinance (Dabi)",
    "branchName": "[HO - BDHO] Head Office",
    "measurementUnit": "Pcs",
    "unitPrice": UNIT_PRICE + ".00",
    "netAssetValue": UNIT_PRICE + ".00",
    "totalDepCalculated": "0.00",
    "utilizationStatusName": "IN_USE",
    "assignUnassignStatus": "UNASSIGNED",
}
# Popup fields of a parent asset that an addition must not change (CR F01S01: purchase value,
# written down value, remaining lifetime and all other information stay as they were)
PARENT_UNCHANGED_FIELDS = [
    "unitPrice", "totalAdditionRegistered", "netAssetValue", "totalDepCalculated", "remainingLife",
    "assetLife", "salvageValue", "depreciationRate", "registrationNumber", "registrationDate",
    "purchaseDate", "itemSpecification", "measurement", "projectName", "branchName",
]
# Popup field that shows the parent asset; only an extended asset has it
PARENT_ASSET_FIELD = "parentAssetSerial"
# Column headings of the Addition History tab, in order (the last two are on the screen but not in the CR)
ADDITION_HISTORY_HEADINGS = [
    "SL", "Asset Serial", "Addition Amount", "Addition Date", "Reference Number", "Item Name",
    "Acc. Depreciation", "WDV", "Impairment Status", "Impairment ID",
]
# Records per page choices of the Addition History tab, and the one chosen when it opens
RECORDS_PER_PAGE_OPTIONS = ["10", "20", "50", "100"]
DEFAULT_RECORDS_PER_PAGE = "10"
# Start of the Reference Number of an addition: the journal voucher posted by HOFIN
REFERENCE_NUMBER_PREFIX = "JV"
# CR F01S01 message when an addition is made to a parent that is in another pending transaction
# (for example an assignment waiting for acknowledgement); {} is the parent's serial
ADDITION_PARENT_PENDING_MESSAGE = "Asset addition is not allowed. Parent asset {} is pending in another transaction flow."
# Note typed when the Global List tests change a Utilization Status
STATUS_NOTE = "AUTOMATION_TEST status sync check"
DAMAGE = "DAMAGE"

# Serial of an existing parent asset for the data-preparation test to add to.
# Leave empty ("") to register a new parent asset first. Example: "FA-000123"
EXISTING_PARENT_SERIAL = "BBDASR00227759"
