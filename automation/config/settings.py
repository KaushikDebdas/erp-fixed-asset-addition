"""
Central place all automation code reads environment/config from.
Never hardcode BASE_URL or credentials anywhere else in the codebase.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "QA")
# Main ERP user and the office (branch) it works in. The older .env names
# (TEST_USERNAME, TEST_PASSWORD, TEST_BRANCH, ERP_BRANCH) are still accepted,
# so an existing .env keeps working.
ERP_USERNAME = os.getenv("ERP_USERNAME") or os.getenv("TEST_USERNAME")
ERP_PASSWORD = os.getenv("ERP_PASSWORD") or os.getenv("TEST_PASSWORD")
# Default branch (office) chosen on the Office Selection screen.
# Optional: leave it empty for a user who has only one office.
DEFAULT_BRANCH = os.getenv("DEFAULT_BRANCH") or os.getenv("ERP_BRANCH") or os.getenv("TEST_BRANCH")

# Second user, the employee an asset is assigned to. Used by the Asset Assign
# Acknowledgement tests, where the assigned user confirms receiving the asset.
# The older names (ASSIGN_USER_USERNAME, ASSIGN_USER_PASSWORD, ASSIGN_USER_BRANCH,
# ASSGN_USER_USERNAME, ASSIGN_USER_PASSWROD) are still accepted.
ASSIGN_ERP_USERNAME = (
    os.getenv("ASSIGN_ERP_USERNAME") or os.getenv("ASSIGN_USER_USERNAME") or os.getenv("ASSGN_USER_USERNAME")
)
ASSIGN_ERP_PASSWORD = (
    os.getenv("ASSIGN_ERP_PASSWORD") or os.getenv("ASSIGN_USER_PASSWORD") or os.getenv("ASSIGN_USER_PASSWROD")
)
ASSIGN_DEFAULT_BRANCH = os.getenv("ASSIGN_DEFAULT_BRANCH") or os.getenv("ASSIGN_USER_BRANCH")
# Employee PIN of the second user. Optional: when empty it is worked out from
# ASSIGN_ERP_USERNAME (see employee_pin_from_username in utils/helpers.py).
ASSIGN_ERP_PIN = os.getenv("ASSIGN_ERP_PIN")

# User who acknowledges an Asset Shipment in the receiving branch. Its default branch IS the
# receiving branch of the shipment. Optional: all three empty = the main user acknowledges in its own branch.
ACK_SHIPMENT_ERP_USERNAME = os.getenv("ACK_SHIPMENT_ERP_USERNAME")
ACK_SHIPMENT_ERP_PASSWORD = os.getenv("ACK_SHIPMENT_ERP_PASSWORD")
ACK_SHIPMENT_ERP_DEFAULT_BRANCH = os.getenv("ACK_SHIPMENT_ERP_DEFAULT_BRANCH") or os.getenv("ACK_SHIPMENT_DEFAULT_BRANCH")

# FAHOV2-643 asset registration / addition flow: HOFIN creator submits the bill,
# HOFA acknowledger acknowledges it, HOFIN approver approves it. HOFIN and HOFA
# are two separate applications, so each has its own URL.
HOFIN_URL = os.getenv("HOFIN_URL")
HOFA_URL = os.getenv("HOFA_URL")
HOFIN_CREATOR_USERNAME = os.getenv("HOFIN_CREATOR_USERNAME")
HOFIN_CREATOR_PASSWORD = os.getenv("HOFIN_CREATOR_PASSWORD")
HOFA_ACK_USERNAME = os.getenv("HOFA_ACK_USERNAME")
HOFA_ACK_PASSWORD = os.getenv("HOFA_ACK_PASSWORD")
HOFIN_APPROVER_USERNAME = os.getenv("HOFIN_APPROVER_USERNAME")
HOFIN_APPROVER_PASSWORD = os.getenv("HOFIN_APPROVER_PASSWORD")

# Additional role credentials for multi-role E2E flows go here as they're
# needed, e.g.:
# HOFA_ERP_USERNAME = os.getenv("HOFA_ERP_USERNAME")
# HOFA_ERP_PASSWORD = os.getenv("HOFA_ERP_PASSWORD")
# HOFA_DEFAULT_BRANCH = os.getenv("HOFA_DEFAULT_BRANCH")

if not BASE_URL:
    raise RuntimeError("BASE_URL not set — check your .env file (see .env.example)")
