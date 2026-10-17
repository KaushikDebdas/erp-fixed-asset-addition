"""
Test data for the asset registration / asset addition flow that starts in HOFIN
(HOFIN creator -> HOFA acknowledger -> HOFIN approver).

Every value was read from the live QA screens (see
`automation/element_catalog/vendor_bill_payable.md`). If QA data changes, change
the value here, in this one file.
"""

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
# Serial of an existing parent asset for the data-preparation test to add to.
# Leave empty ("") to register a new parent asset first. Example: "FA-000123"
EXISTING_PARENT_SERIAL = "BBDASR00227727"
