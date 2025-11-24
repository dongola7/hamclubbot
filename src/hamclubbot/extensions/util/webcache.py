# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

"""Implements a basic cache for web requests"""

import logging
import time
import asyncio

import requests

logger = logging.getLogger(__name__)

class CacheEntry:
    """Represents an entry in the WebCache"""

    def __init__(self, content: bytes, ttl: float):
        self.__created_at = time.time()
        self.__expires_at = self.__created_at + ttl
        self.__content = content
        self.__extra = None

    @property
    def created_at(self) -> float:
        """Returns the timestamp at which the cache entry was created"""
        return self.__created_at

    @property
    def expires_at(self) -> float:
        """Returns the timestamp at which the cache entry expires"""
        return self.__expires_at

    @property
    def content(self) -> bytes:
        """Returns the raw content of the cache entry (as retrieved from the URL)"""
        return self.__content

    @property
    def extra(self) -> object | None:
        """Returns the 'extra' field of the cache. Used to store custom data with the entry"""
        return self.__extra

    @extra.setter
    def extra(self, value: object | None):
        self.__extra = value

    def last_refreshed_str(self) -> str:
        """Returns a string indicating the amount of time since the last refresh."""
        last_refreshed = round((time.time() - self.created_at) / 60)
        if last_refreshed == 0:
            return "Just refreshed"
        if last_refreshed == 1:
            return "Refreshed 1 minute ago"
        return f"Refreshed {last_refreshed} minutes ago"

class WebCache:
    """Implements a simple cache for web content"""

    def __init__(self, cache_expiry_seconds = 900):
        """
        Constructor

        Args:
            cache_expiry_seconds (int): The number of seconds before a cache entry expires
            (default = 900 (15 Minutes))
        """
        self.__cache = dict[str, CacheEntry]()
        self.__cache_expiry_seconds = cache_expiry_seconds

    async def get_url(self, url: str) -> CacheEntry:
        """
        Returns the cache entry for the given URL.

        Returns:
            dict: Dictionary of the cache entry. All cache entries have a 'timestamp' and a
                'content' key. The 'timestamp' is the time the cache entry was created. The
                'content' is the binary content returned from the URL. Optionally, some cache
                entries may also have an 'extra' key which stores user defined data. You can set
                the 'extra' content using the cacheRelatedData method.
        """
        # Check if URL is cached and the cache has not yet expired.
        if url in self.__cache:
            cache_entry = self.__cache[url]
            timestamp = time.time()
            if timestamp < cache_entry.expires_at:
                logger.debug("returning cached content for %s", url)
                # Cache has not expired, returned cached content
                return cache_entry

        # Cache has either expired or URL is not in cache. Retrieve it
        # and add to cache
        logger.debug("retrieving content for %s", url)
        resp = await asyncio.get_event_loop().run_in_executor(None, requests.get, url)
        cache_entry = self.__cache[url] = CacheEntry(resp.content, self.__cache_expiry_seconds)

        return cache_entry

    def clear_cache(self, url: str) -> None:
        """Clears the cache entry for the given URL. Next time a request is made,
        the URL will be directly retrieved"""
        if url in self.__cache:
            del self.__cache[url]
