"""
write_off_flow.py: one reusable step used by the Asset Write-off tests.

A write-off only accepts an asset whose Utilization Status is not IN_USE.
`create_write_off` registers and approves a new Furniture asset (the same way
test_01 does, with `registrations.get_approved`), marks it DAMAGE, fills the
Asset Write-off form and saves it with Draft or Submit. Every test passes its
own `owner` name, so each test gets its own new asset (a written-off asset
cannot be used again) and the saved assets of test_01 are not touched.
"""
from pages.asset_serial_global_list_page import AssetSerialGlobalListPage
from pages.asset_write_off_page import AssetWriteOffPage
from test_data.asset_registration_data import PROFILE_NAMES_BY_ITEM
from utils.registration_helper import RegistrationHelper

# The notes typed on the Global List popup and on the write-off form
STATUS_NOTE = "AUTOMATION_TEST damaged for write off"
WRITE_OFF_NOTE = "write off"


def create_write_off(
    registrations: RegistrationHelper,
    global_list_page: AssetSerialGlobalListPage,
    write_off_page: AssetWriteOffPage,
    owner: str,
    save_as: str,
) -> dict:
    """
    Write off a new approved Furniture asset. `owner` is a name made up by the
    test (for example "write_off_reject") that gives it its own asset; `save_as`
    is "draft" or "submit". Returns {"serial", "item_name"}.
    """
    # A new approved asset (registered and approved now)
    record = registrations.get_approved("furniture", "spot", owner)
    serial = record["serial"]
    item_name = PROFILE_NAMES_BY_ITEM["furniture"][0]

    # Set its Utilization Status to DAMAGE
    global_list_page.mark_asset_damaged(serial, STATUS_NOTE)

    # Fill the write-off form and add the asset to the grid
    write_off_page.navigate_here()
    write_off_page.select_project(record["data"]["project"])
    write_off_page.select_asset(serial, serial)
    write_off_page.enter_note(WRITE_OFF_NOTE)
    write_off_page.add_to_grid()
    write_off_page.verify_grid_row(serial, item_name, "DAMAGE", WRITE_OFF_NOTE)

    # Save it
    if save_as == "draft":
        write_off_page.draft_and_verify()
    else:
        write_off_page.submit_and_verify()
    return {"serial": serial, "item_name": item_name}
