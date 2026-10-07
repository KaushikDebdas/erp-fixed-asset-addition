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
from utils.helpers import unique_name


# Name the approved asset that is transferred is saved under in test_data/saved_assets.json
# (utils/transfer_helper.py, SavedTransferHelper); it is removed once its serial is added to a challan
TRANSFER_ASSET_GROUP = "transfer_saved"


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


def build_challan_data(quantity: int = 1) -> dict:
    """
    Return values for the Create Challan popup: a transfer inside Head Office
    from project [015] to project [060] Progoti, of one Cabinet Table.

    The To Project is [060] Progoti because other projects (for example
    [C04] Administratiion) are not mapped and Draft is refused with
    "Area code not found".
    """
    return {
        "from_project": "[015] Microfinance (Dabi)",
        "receiving_branch_search": "Head",
        "receiving_branch": "Head Office",
        "to_project_search": "Progoti",
        "to_project": "[060] Progoti",
        "item_search": "Cabinet",
        "item_name": "Cabinet Table",
        "quantity": quantity,
        "note": "AUTOMATION_TEST challan note",
    }
