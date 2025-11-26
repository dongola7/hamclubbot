# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

import time
from unittest.mock import MagicMock

from hamclubbot.extensions.util.webcache import CacheEntry

def test_expires_at_populated():
    entry = CacheEntry(b'', 60)
    assert entry.expires_at == entry.created_at + 60, "expiration time is creation time plus 60 seconds"

def test_last_refreshed_str(monkeypatch):
    entry = CacheEntry(b'', 600)

    monkeypatch.setattr(time, 'time', MagicMock(return_value = entry.created_at))
    assert entry.last_refreshed_str() == "Just refreshed", "refreshed 0 minutes ago"

    monkeypatch.setattr(time, 'time', MagicMock(return_value = entry.created_at + 59))
    assert entry.last_refreshed_str() == "Just refreshed", "refreshed <1 minute ago"

    monkeypatch.setattr(time, 'time', MagicMock(return_value = entry.created_at + 60))
    assert entry.last_refreshed_str() == "Refreshed 1 minute ago", "refreshed exactly 1 minute ago"

    monkeypatch.setattr(time, 'time', MagicMock(return_value = entry.created_at + 119))
    assert entry.last_refreshed_str() == "Refreshed 1 minute ago", "refreshed 1 minute ago"

    monkeypatch.setattr(time, 'time', MagicMock(return_value = entry.created_at + 120))
    assert entry.last_refreshed_str() == "Refreshed 2 minutes ago", "refreshed >1 minute ago"

    monkeypatch.setattr(time, 'time', MagicMock(return_value = entry.created_at + 600))
    assert entry.last_refreshed_str() == "Refreshed 10 minutes ago", "refreshed 10 minutes ago"
