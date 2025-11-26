# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

import time
import pytest
from unittest.mock import call, MagicMock, PropertyMock

import requests

from hamclubbot.extensions.util.webcache import CacheEntry, WebCache

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

@pytest.fixture
def mock_response(monkeypatch):
    """monkeypatches requests.get and provides a basic mock response object"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    type(mock_response).content = PropertyMock(return_value = 'some mock content')
    monkeypatch.setattr(requests, 'get', MagicMock(return_value = mock_response))
    yield mock_response

async def test_get_url_not_in_cache(mock_response):
    cache = WebCache(60)
    entry = await cache.get_url('http://localhost')

    requests.get.assert_called_once_with('http://localhost')
    assert entry.content == 'some mock content', 'cache entry missing expected content'

async def test_get_url_in_cache(mock_response):
    cache = WebCache(60)

    # Make two queries. The first populates the cache, the second should reuse the cache
    await cache.get_url('http://localhost')
    entry = await cache.get_url('http://localhost')

    requests.get.assert_called_once_with('http://localhost') # should only be called once
    assert entry.content == 'some mock content', 'cache entry missing expected content'

async def test_get_url_expired_cache(mock_response, monkeypatch):
    cache = WebCache(60)

    # Populate the cache to start
    entry = await cache.get_url('http://localhost')

    # monkeypatch the current time to reflect expiry
    monkeypatch.setattr(time, 'time', MagicMock(return_value = entry.expires_at + 1))

    # Get the URL a second time
    type(mock_response).content = PropertyMock(return_value = 'some different mock content')
    entry = await cache.get_url('http://localhost')
    
    requests.get.assert_has_calls([call('http://localhost'), call('http://localhost')])
    assert entry.content == 'some different mock content', 'cache entry missing expected content'

async def test_clear_cache(mock_response):
    cache = WebCache(60)

    # Populate the cache to start
    entry = await cache.get_url('http://localhost')

    # Clear the cache
    cache.clear_cache('http://localhost')

    # Get the URL a second time
    type(mock_response).content = PropertyMock(return_value = 'some different mock content')
    entry = await cache.get_url('http://localhost')
    
    requests.get.assert_has_calls([call('http://localhost'), call('http://localhost')])
    assert entry.content == 'some different mock content', 'cache entry missing expected content'
