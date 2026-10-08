"""
sale_flow.py: one reusable step used by the Asset Sale tests.

The asset sold is one of the approved assets that test_01 creates (the "ten AAQ
assets", saved in test_data/saved_assets.json and read with
`registrations.get_approved`). It is UNASSIGNED and IN_USE, which is what the
Asset Sale screen needs; its status is not changed.

A sold asset cannot be sold again, so `create_sale` removes it from the saved
assets once the sale is saved (a later run then registers a new one).
"""
from pages.asset_sale_page import AssetSalePage
from test_data.asset_registration_data import AAQ_ASSET_GROUP
from utils.registration_helper import RegistrationHelper

SALE_NOTE = "sale"


def create_sale(
    registrations: RegistrationHelper, sale_page: AssetSalePage, item: str, sub_type: str, sale_change: int, save_as: str
) -> dict:
    """
    Sell the approved AAQ asset of this item and sub type ("furniture", "gift").
    `sale_change` is added to the Written Down Value to get the Sale Value (+5000
    sells above it, -5000 below it); `save_as` is "draft" or "submit".
    Returns {"serial", "sale_value", "profit_loss"}.
    """
    # The approved asset made by test_01 (registered now when none is saved)
    record = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)
    serial = record["serial"]

    # Open the sale form, choose the project and the asset
    sale_page.navigate_here()
    sale_page.select_project(record["data"]["project"])
    sale_page.select_asset(serial, serial)

    # Enter the Sale Value and Add to Grid
    sale_value = sale_page.get_written_down_value() + sale_change
    sale_page.enter_sale_value(sale_value)
    sale_page.enter_note(SALE_NOTE)
    sale_page.add_to_grid()
    sale_page.verify_sale_grid_row(serial, sale_value, sale_change)

    # Save it, then forget the asset: it is used up
    if save_as == "draft":
        sale_page.draft_and_verify()
    else:
        sale_page.submit_and_verify()
    registrations.forget(record, "APPROVED", AAQ_ASSET_GROUP)
    return {"serial": serial, "sale_value": sale_value, "profit_loss": sale_change}
