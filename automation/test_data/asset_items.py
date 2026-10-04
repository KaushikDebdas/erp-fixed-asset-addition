"""
asset_items.py: the asset items every Asset Registration test is run for,
shared by the AAQ, List and Approval List test files.

Put one of these above a test and it runs once per item. The test name shows
the item, e.g. test_...[land]. To run one item:
    pytest tests/test_01_asset_registration_aaq.py -k "land"
"""
import pytest

from test_data.asset_registration_data import ITEM_NAMES

# All five items
ASSET_ITEMS = pytest.mark.parametrize("item", ITEM_NAMES)

# Land has no minimum unit price; the other items must be 20,000 Taka or more
MINIMUM_PRICE_ITEMS = pytest.mark.parametrize("item", ["furniture", "building", "laptop", "desktop"])

# Land and Building need a Measurement above zero
MEASURED_ITEMS = pytest.mark.parametrize("item", ["land", "building"])
