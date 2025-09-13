import datetime
import requests
import logging

logger = logging.getLogger(__name__)

class WebCache:
    """Implements a simple cache for web content"""

    def __init__(self, cache_expiry_seconds = 900):
        """
        Constructor

        Args:
            cache_expiry_seconds (int): The number of seconds before a cache entry expires (default = 900 (15 Minutes))
        """
        self.__cache = dict()
        self.__CACHE_EXPIRY_TIME = datetime.timedelta(seconds = cache_expiry_seconds)

    def getUrl(self, url: str):
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
            timestamp = datetime.datetime.now()
            if timestamp - cache_entry['timestamp'] < self.__CACHE_EXPIRY_TIME:
                logger.debug(f"returning cached content for {url}")
                # Cache has not expired, returned cached content
                return cache_entry

        # Cache has either expired or URL is not in cache. Retrieve it
        # and add to cache            
        logger.debug(f"retrieving content for {url}")
        resp = requests.get(url)
        cache_entry = self.__cache[url] = {
            'timestamp': datetime.datetime.now(),
            'content': resp.content
        }
        
        return cache_entry
    
    def cacheRelatedData(self, url: str, data: object):
        """
        Sets the 'extra' value of the cache entry for the given URL

        Raises:
            ValueError: If the URL does not exist in the cache
        """
        if url in self.__cache:
            if (data == None) and ('extra' in self.__cache['url']):
                del self.__cache[url]['extra']
            else:
                self.__cache[url]['extra'] = data
        else:
            raise ValueError(f'{url} is not in the cache')