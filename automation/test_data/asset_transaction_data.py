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
ACKNOWLEDGE_TOAST = "Acknowledged successfully"
