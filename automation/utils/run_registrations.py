"""
run_registrations.py: the dictionary that remembers the registrations of ONE test run.

`RegistrationHelper` (utils/registration_helper.py) keeps the registrations it made in this
dictionary, under the key (item, sub type, status, owner), so a later test finds them. The
owner is the asset slot name (test_data/asset_slots.py), for example "sale_profit_a".

It behaves like a plain dictionary, with one addition: `trusted` is the set of keys that
are known to be up to date, because they were made or changed during this run. Nothing is
saved between runs: every run starts with new assets.
"""


class RunRegistrations(dict):
    """A dictionary of registration records for one run, with the set of keys known to be current."""

    def __init__(self):
        super().__init__()
        # Keys made or changed during this run
        self.trusted = set()

    def __setitem__(self, key, record) -> None:
        """Add or replace a record. A record put here during the run is up to date, so it is trusted."""
        super().__setitem__(key, record)
        self.trusted.add(key)

    def pop(self, key, default=None):
        """Remove a record."""
        self.trusted.discard(key)
        return super().pop(key, default)

    def setdefault(self, key, record):
        """Add a record only when the key is not there yet."""
        if key not in self:
            self[key] = record
        return self[key]
