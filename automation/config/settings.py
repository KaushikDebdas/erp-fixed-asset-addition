"""
Central place all automation code reads environment/config from.
Never hardcode BASE_URL or credentials anywhere else in the codebase.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
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

# Additional role credentials for multi-role E2E flows go here as they're
# needed, e.g.:
# HOFA_USERNAME = os.getenv("HOFA_USERNAME")
# HOFA_PASSWORD = os.getenv("HOFA_PASSWORD")

if not BASE_URL:
    raise RuntimeError("BASE_URL not set — check your .env file (see .env.example)")
