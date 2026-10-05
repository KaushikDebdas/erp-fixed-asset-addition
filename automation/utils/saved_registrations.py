"""
saved_registrations.py: remembers registrations for the tests, and saves the
ones of the 10 AAQ assets in a file, so a later run can reuse them instead of
creating them again.

How it works:
    SavedRegistrations behaves like the plain dictionary the registration
    helper (utils/registration_helper.py) has always used. The difference:
    - when it is created it loads test_data/saved_assets.json, and
    - every time a record of the group AAQ_ASSET_GROUP or AAQ_PENDING_GROUP is added, changed or
      removed, the file is written again.
    Records of any other owner stay in memory only, because other tests use
    those assets up (assign, transfer, ...) and need a fresh one every run.

    A record loaded from the file may be out of date (someone approved or
    changed it since). The helper therefore checks its real status in the
    Registration List the first time a run uses it (see `trusted` below).

The file holds staging registration numbers, so it is not committed to git.
Delete it to start again: every asset is then created again.
"""
import json
from pathlib import Path

from test_data.asset_registration_data import AAQ_ASSET_GROUP, AAQ_PENDING_GROUP

# Where the saved records are kept
SAVED_FILE = Path(__file__).resolve().parent.parent / "test_data" / "saved_assets.json"

# Only records of these owners are saved in the file
SAVED_OWNERS = [AAQ_ASSET_GROUP, AAQ_PENDING_GROUP]


class SavedRegistrations(dict):
    """A dictionary of registration records that saves the 10 AAQ assets in a file."""

    def __init__(self, file_path: Path = SAVED_FILE):
        super().__init__()
        self.file_path = file_path
        # Keys whose status was created or checked during this run (not just loaded from the file)
        self.trusted = set()
        self.load()

    def load(self) -> None:
        """Read the saved records, if the file exists."""
        if not self.file_path.exists():
            return
        try:
            entries = json.loads(self.file_path.read_text(encoding="utf-8"))
        except ValueError:
            return
        for entry in entries:
            super().__setitem__(tuple(entry["key"]), entry["record"])

    def save(self) -> None:
        """Write the records of the saved owners to the file."""
        entries = []
        for key, record in self.items():
            if key[3] in SAVED_OWNERS:
                entries.append({"key": list(key), "record": record})
        self.file_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def __setitem__(self, key, record) -> None:
        """Add or replace a record. A record put here during a run is up to date, so it is trusted."""
        super().__setitem__(key, record)
        self.trusted.add(key)
        self.save()

    def pop(self, key, default=None):
        """Remove a record and save."""
        record = super().pop(key, default)
        self.trusted.discard(key)
        self.save()
        return record

    def setdefault(self, key, record):
        """Add a record only when the key is not there yet."""
        if key not in self:
            self[key] = record
        return self[key]
