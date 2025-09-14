import datetime
import requests
import logging
import time

logger = logging.getLogger(__name__)

class CacheEntry:
    def __init__(self, content: bytes):
        self.__timestamp = time.time()
        self.__content = content
        self.__extra = None
    
    @property
    def timestamp(self) -> float:
        return self.__timestamp
    
    @property
    def content(self) -> bytes:
        return self.__content
    
    @property
    def extra(self) -> object | None:
        return self.__extra
    
    @extra.setter
    def extra(self, value: object | None):
        self.__extra = value
    
    


class WebCache:
    """Implements a simple cache for web content"""

    def __init__(self, cache_expiry_seconds = 900):
        """
        Constructor

        Args:
            cache_expiry_seconds (int): The number of seconds before a cache entry expires (default = 900 (15 Minutes))
        """
        self.__cache = dict[str, CacheEntry]()
        self.__CACHE_EXPIRY_TIME = cache_expiry_seconds

    def getUrl(self, url: str) -> CacheEntry:
        """
        Returns the cache entry for the given URL.

        Returns:
            dict: Dictionary of the cache entry. All cache entries have a 'timestamp' and a 'content'
                key. The 'timestamp' is the time the cache entry was created. The 'content' is the binary
                content returned from the URL. Optionally, some cache entries may also have an 'extra' key
                which stores user defined data. You can set the 'extra' content using the cacheRelatedData
                method.
        """
        # Check if URL is cached and the cache has not yet expired.
        if url in self.__cache:
            cache_entry = self.__cache[url]
            timestamp = time.time()
            if timestamp - cache_entry.timestamp < self.__CACHE_EXPIRY_TIME:
                logger.debug(f"returning cached content for {url}")
                # Cache has not expired, returned cached content
                return cache_entry

        # Cache has either expired or URL is not in cache. Retrieve it
        # and add to cache            
        logger.debug(f"retrieving content for {url}")
        resp = requests.get(url)
        cache_entry = self.__cache[url] = CacheEntry(resp.content)
        
        return cache_entry