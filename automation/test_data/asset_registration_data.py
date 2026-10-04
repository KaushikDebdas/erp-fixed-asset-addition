"""
asset_registration_data.py: the test data used to create an Asset
Registration (AAQ), shared by every Asset Registration test file.

Why one file: the AAQ, List and Approval List tests all start by creating a
registration. Keeping the values here means a change (for example a
different project) is made in ONE place.

How to use it:
    data = build_asset_data("land")                      # a Land registration
    data = build_asset_data("laptop", quantity=3)        # change the quantity
    data = build_asset_data("furniture", sub_type="gift")  # Gift Item
The five items are: furniture, land, building, laptop, desktop.
"""
from utils.helpers import unique_name

# One entry per asset item.
#   search:      what is typed into the Asset Item Name search box
#   selected:    the start of the result that is clicked
#   grid_name:   the name the grids and the popup show for the item
#   spec_prefix: the start of the Item Specification (a unique ending is added)
#   measurement: the Measurement typed in; "" means this item has none
ITEM_TABLE = {
    "furniture": {
        "search": "Furniture",
        "selected": "Cabinet Table",
        "grid_name": "Cabinet Table",
        "spec_prefix": "AUTOMATION_TEST-SPEC-FURN",
        "measurement": "",
    },
    "land": {
        "search": "Land",
        "selected": "Land-> Land-> Land-> Land",
        "grid_name": "Land",
        "spec_prefix": "AUTOMATION_TEST-SPEC-LAND",
        "measurement": "12.5",
    },
    "building": {
        "search": "Building",
        "selected": "Building-> Building-> Building-> Building",
        "grid_name": "Building",
        "spec_prefix": "AUTOMATION_TEST-SPEC-BUILDING",
        "measurement": "15.5",
    },
    "laptop": {
        "search": "Laptop",
        "selected": "Laptop-> Laptop-> Laptop-> Computer/Laptop",
        "grid_name": "Laptop",
        "spec_prefix": "AUTOMATION_TEST-SPEC-LAPTOP",
        "measurement": "",
    },
    "desktop": {
        "search": "Desktop Computer",
        "selected": "Desktop Computer-> Computer-> Computer-> Computer/Laptop",
        "grid_name": "Desktop Computer",
        "spec_prefix": "AUTOMATION_TEST-SPEC-DESKTOP",
        "measurement": "",
    },
}

# The item names, in the order the tests run them
ITEM_NAMES = list(ITEM_TABLE)


def build_asset_data(
    item: str = "furniture",
    quantity: int = 1,
    unit_price: int = 25000,
    measurement: str = "",
    sub_type: str = "spot",
) -> dict:
    """
    Return a fresh set of registration values for one asset item.

    item:        furniture, land, building, laptop or desktop
    quantity:    how many units
    unit_price:  price of one unit in Taka
    measurement: leave empty to use the item's own Measurement (Land 12.5,
                 Building 15.5, the others none); pass a value to change it
    sub_type:    "spot" for Spot Purchase or "gift" for Gift Item

    The Item Specification is unique on every call, so each registration a
    test creates can be told apart from the ones made by earlier runs.
    """
    details = ITEM_TABLE[item]
    data = {
        "item": item,
        "project": "[015] Microfinance (Dabi)",
        "sub_type": sub_type,
        "remarks": "AUTOMATION_TEST registration note",
        "vendor": "ACE IT[P008937]",
        # The View popup shows the vendor's name and number in separate fields
        "vendor_name": "ACE IT",
        "vendor_number": "P008937",
        "asset_item_search": details["search"],
        "asset_item_selected": details["selected"],
        "grid_item_name": details["grid_name"],
        "item_specification": unique_name(details["spec_prefix"]),
        "quantity": quantity,
        "unit_price": unit_price,
    }
    # Only items that have a Measurement get the key
    chosen_measurement = measurement or details["measurement"]
    if chosen_measurement:
        data["measurement"] = chosen_measurement
    return data


def build_registration_data(
    quantity: int = 1, unit_price: int = 25000, measurement: str = "", sub_type: str = "spot"
) -> dict:
    """
    Return the default registration (a Furniture asset), used by the smoke tests.
    The quantity, unit price and sub type can be changed, e.g.
    build_registration_data(unit_price=19999) or build_registration_data(sub_type="gift").
    """
    return build_asset_data("furniture", quantity, unit_price, measurement, sub_type)


def build_land_asset_data() -> dict:
    """Return a Land registration with a Measurement, used to prepare splittable assets."""
    return build_asset_data("land")
