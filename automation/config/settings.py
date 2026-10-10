"""
Central place all automation code reads environment/config from.
Never hardcode URLs or credentials anywhere else in the codebase.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# HOFA is the Fixed Asset application. Every Fixed Asset test opens it, so BASE_URL
# below is simply HOFA_URL. HOFIN is the finance application used only by the
# asset registration / addition flow.
HOFA_URL = os.getenv("HOFA_URL")
HOFIN_URL = os.getenv("HOFIN_URL")
BASE_URL = HOFA_URL
ENVIRONMENT = os.getenv("ENVIRONMENT", "QA")
TEST_USERNAME = os.getenv("TEST_USERNAME")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")

# Second user, the employee an asset is assigned to. Used by the Asset Assign
# Acknowledgement tests, where the assigned user confirms receiving the asset.
# The .env names are ASSIGN_USER_USERNAME and ASSIGN_USER_PASSWORD. The older
# misspelled names (ASSGN_USER_USERNAME, ASSIGN_USER_PASSWROD) are still
# accepted, so an existing .env keeps working.
ASSIGN_USER_USERNAME = os.getenv("ASSIGN_USER_USERNAME") or os.getenv("ASSGN_USER_USERNAME")
ASSIGN_USER_PASSWORD = os.getenv("ASSIGN_USER_PASSWORD") or os.getenv("ASSIGN_USER_PASSWROD")

# Three logins of the asset registration / addition flow (FAHOV2-643):
# HOFIN creator -> HOFA acknowledger -> HOFIN approver. HOFA_ACKNOWLEDGER_* is
# also accepted for the acknowledger.
HOFIN_CREATOR_USERNAME = os.getenv("HOFIN_CREATOR_USERNAME")
HOFIN_CREATOR_PASSWORD = os.getenv("HOFIN_CREATOR_PASSWORD")
HOFA_ACK_USERNAME = os.getenv("HOFA_ACK_USERNAME") or os.getenv("HOFA_ACKNOWLEDGER_USERNAME")
HOFA_ACK_PASSWORD = os.getenv("HOFA_ACK_PASSWORD") or os.getenv("HOFA_ACKNOWLEDGER_PASSWORD")
HOFIN_APPROVER_USERNAME = os.getenv("HOFIN_APPROVER_USERNAME")
HOFIN_APPROVER_PASSWORD = os.getenv("HOFIN_APPROVER_PASSWORD")

if not HOFA_URL:
    raise RuntimeError("HOFA_URL not set — check your .env file (see .env.example)")
