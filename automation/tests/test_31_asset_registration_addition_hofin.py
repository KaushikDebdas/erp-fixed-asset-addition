"""
test_32_asset_registration_addition_hofin.py: the asset registration and the
asset addition that start in HOFIN (CR FAHOV2-643).

Flow: projects/fixedasset/e2e-flows/asset-registration-addition-hofin-hofa-hofin.md

    HOFIN creator submits a vendor bill  ->  HOFA acknowledger acknowledges it
    ->  HOFIN approver approves it

Two tests, run in this order:
    1. Section A: registration. A new parent asset is created. Its serial is
       left in `hofin_flow_data` for the next test.
    2. Section B: addition. A second bill adds to that parent asset. The new
       extended asset is checked in the HOFA Asset Serial Global List.

A third test prepares data on its own: it registers a new parent asset and adds
DATA_PREP_EXTENDED_COUNT (4) extended assets to it, then prints all the serials.

Logins (HOFIN creator, HOFA acknowledger, HOFIN approver) and both URLs come
from .env. To run the two flow tests, run test 1 first, or the whole file:
    pytest tests/test_32_asset_registration_addition_hofin.py
To prepare data only (works alone, from any folder state):
    pytest tests/test_32_asset_registration_addition_hofin.py -m data_prep
"""
import pytest

from test_data import hofin_asset_data as data
from utils.helpers import unique_name


@pytest.mark.regression
def test_asset_registration_hofin_hofa_hofin(hofin_flow, hofin_flow_data):
    """
    Flow "Asset Registration & Asset Addition (HOFIN > HOFA > HOFIN)", Section A:
    a bill submitted in HOFIN, acknowledged in HOFA and approved in HOFIN
    creates a new parent asset in the HOFA Asset Serial Global List.
    """
    # Step 1: the HOFIN creator submits a vendor bill with a fixed asset item
    transaction_no = hofin_flow.create_bill(unique_name("REG"))

    # Step 2: the HOFA acknowledger acknowledges that bill
    hofin_flow.acknowledge(transaction_no)

    # Step 3: the HOFIN approver approves that bill
    hofin_flow.approve(transaction_no)

    # Step 4: the new parent asset is the newest asset of the Global List
    global_list = hofin_flow.open_hofa_global_list()
    parent_serial = global_list.read_newest_parent_serial(data.ASSET_ITEM_NAME)
    global_list.search_by_serial(parent_serial)
    global_list.verify_statuses(parent_serial, "UNASSIGNED", "IN_USE")
    hofin_flow.take_screenshot(global_list.page, f"new parent asset {parent_serial}")

    # Step 5: keep the parent asset serial for the addition test
    hofin_flow_data["parent_serial"] = parent_serial


@pytest.mark.regression
def test_asset_addition_hofin_hofa_hofin(hofin_flow, hofin_flow_data):
    """
    Flow "Asset Registration & Asset Addition (HOFIN > HOFA > HOFIN)", Section B:
    an addition to the parent asset created by the registration test creates a
    separate extended asset "<parent serial>-1" that points to its parent.
    """
    parent_serial = hofin_flow_data.get("parent_serial", "")
    assert parent_serial != "", (
        "No parent asset serial. Run test_asset_registration_hofin_hofa_hofin first."
    )
    extended_serial = parent_serial + data.FIRST_EXTENSION_SUFFIX

    # Step 1: the HOFIN creator submits a bill that adds to the parent asset
    transaction_no = hofin_flow.create_bill(unique_name("ADD"), parent_serial)

    # Step 2: the HOFA acknowledger acknowledges the addition
    hofin_flow.acknowledge(transaction_no)

    # Step 3: the HOFIN approver approves the addition
    hofin_flow.approve(transaction_no)

    # Step 4: the extended asset is listed on its own, with the parent's item
    global_list = hofin_flow.open_hofa_global_list()
    global_list.search_by_serial(extended_serial)
    global_list.verify_statuses(extended_serial, "UNASSIGNED", "IN_USE")
    hofin_flow.take_screenshot(global_list.page, f"extended asset {extended_serial}")

    # Step 5: the extended asset shows its parent and has no Addition History tab
    global_list.verify_extended_asset_popup(extended_serial, parent_serial)

    # Step 6: the parent asset lists the extended asset in its Addition History tab
    global_list.search_by_serial(parent_serial)
    global_list.verify_parent_addition_history(
        parent_serial,
        extended_serial,
        {"Addition Amount": data.UNIT_PRICE, "Item Name": data.ASSET_ITEM_NAME},
    )
    hofin_flow.take_screenshot(global_list.page, "parent asset addition history checked")

    # Step 7: keep the extended asset serial for the tests of other screens
    hofin_flow_data["extended_serial"] = extended_serial

# @pytest.mark.skip(reason="data prep test is not part of the flow, and is skipped by default")
@pytest.mark.data_prep
def test_prepare_parent_with_extended_assets(hofin_flow, hofin_flow_data):
    """
    Data preparation for the "Asset Registration & Asset Addition (HOFIN > HOFA >
    HOFIN)" flow: adds DATA_PREP_EXTENDED_COUNT extended assets to the parent asset
    EXISTING_PARENT_SERIAL, or to a new parent asset when that is empty.
    Needs no other test to run first.
    """
    parent_serial = data.EXISTING_PARENT_SERIAL

    # Step 1: with no existing parent, register a new parent asset
    if parent_serial == "":
        parent_serial = hofin_flow.create_parent_asset()

    # Step 2: add the extended assets to the parent asset
    for number in range(data.DATA_PREP_EXTENDED_COUNT):
        hofin_flow.add_extended_asset(parent_serial)

    # Step 3: check that the parent asset is listed in the HOFA Global List
    global_list = hofin_flow.open_hofa_global_list()
    global_list.search_by_serial(parent_serial)
    hofin_flow.take_screenshot(global_list.page, f"parent asset {parent_serial} with new extended assets")

    # Step 4: show the prepared parent serial in the terminal
    print(f"\nPREPARED DATA: parent asset {parent_serial} with {data.DATA_PREP_EXTENDED_COUNT} new extended assets")

    # Step 5: keep the parent serial for any later test in the same run
    hofin_flow_data["parent_serial"] = parent_serial
