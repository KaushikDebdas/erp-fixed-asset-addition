"""
asset_shipment_data.py: the test data used to create an Asset Shipment and its
Transfer Challan, shared by the Asset Transfer test files.

Why one file: the Shipment, Challan, Approval and Acknowledge tests all start
from the same shipment. Keeping the values here means a change (for example a
different To Project) is made in ONE place.

How to use it:
    shipment = build_shipment_data()
    challan = build_challan_data()
"""
from config.settings import ACK_SHIPMENT_ERP_DEFAULT_BRANCH
from utils.helpers import unique_name

# The scenarios of a transfer (which branch it goes to and how its projects relate)
SAME_BRANCH_DIFFERENT_PROJECT = "same_branch_different_project"
OTHER_BRANCH_SAME_PROJECT = "other_branch_same_project"
OTHER_BRANCH_DIFFERENT_PROJECT = "other_branch_different_project"

# The OTHER_BRANCH scenarios go to the default branch of the shipment acknowledgement user
# (ACK_SHIPMENT_ERP_* in .env)

# From Project is the project of the transferred asset. The To Project must be mapped for the
# receiving branch, or Draft is refused with "Area code not found".
SCENARIO_PROJECTS = {
    SAME_BRANCH_DIFFERENT_PROJECT: {
        "from_project": "[015] Microfinance (Dabi)",
        "to_project_search": "Progoti",
        "to_project": "[060] Progoti",
    },
    OTHER_BRANCH_SAME_PROJECT: {
        "from_project": "[015] Microfinance (Dabi)",
        "to_project_search": "Microfinance",
        "to_project": "[015] Microfinance (Dabi)",
    },
    OTHER_BRANCH_DIFFERENT_PROJECT: {
        "from_project": "[015] Microfinance (Dabi)",
        "to_project_search": "Progoti",
        "to_project": "[060] Progoti",
    },
}


def build_shipment_data() -> dict:
    """
    Return fresh values for the Create Shipment popup.

    The courier name is unique on every call, so a shipment created by one run
    can be told apart from the ones created by earlier runs.
    """
    return {
        "courier_name": unique_name("AUTOMATION_TEST courier"),
        "courier_number": "AWB-AUTOTEST-1",
        "driver_name": "AUTOMATION_TEST driver",
        "transport_no": "TR-AUTOTEST-1",
        "courier_details": "AUTOMATION_TEST courier details",
        "remarks": "AUTOMATION_TEST shipment note",
    }


def build_challan_data(quantity: int = 1, scenario: str = SAME_BRANCH_DIFFERENT_PROJECT) -> dict:
    """
    Return values for the Create Challan popup: one Cabinet Table, with the
    projects of the scenario (SCENARIO_PROJECTS).

    The receiving branch is "" for SAME_BRANCH_DIFFERENT_PROJECT, which means the sending branch (the
    popup shows it). For the other scenarios it is the default branch of the shipment
    acknowledgement user (ACK_SHIPMENT_ERP_DEFAULT_BRANCH in .env).
    """
    projects = SCENARIO_PROJECTS[scenario]
    receiving_branch = ""
    if scenario != SAME_BRANCH_DIFFERENT_PROJECT:
        receiving_branch = ACK_SHIPMENT_ERP_DEFAULT_BRANCH or ""
    return {
        "scenario": scenario,
        "from_project": projects["from_project"],
        "receiving_branch": receiving_branch,
        "to_project_search": projects["to_project_search"],
        "to_project": projects["to_project"],
        "item_search": "Cabinet",
        "item_name": "Cabinet Table",
        "quantity": quantity,
        "note": "AUTOMATION_TEST challan note",
    }
