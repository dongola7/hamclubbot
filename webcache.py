import datetime
import requests
import logging

class WebCache:
    def __init__(self, cache_expiry_seconds = 900):
        self.__cache = dict()
        self.__CACHE_EXPIRY_TIME = datetime.timedelta(seconds = cache_expiry_seconds)
        self.__log = logging.getLogger('webcache')

    def getUrl(self, url: str):
        # Check if URL is cached and the cache has not yet expired.
        if url in self.__cache:
            cache_entry = self.__cache[url]
            timestamp = datetime.datetime.now()
            if timestamp - cache_entry['timestamp'] < self.__CACHE_EXPIRY_TIME:
                self.__log.debug(f"returning cached content for {url}")
                # Cache has not expired, returned cached content
                return cache_entry

        # Cache has either expired or URL is not in cache. Retrieve it
        # and add to cache            
        self.__log.debug(f"retrieving content for {url}")
        resp = requests.get(url)
        cache_entry = self.__cache[url] = {
            'timestamp': datetime.datetime.now(),
            'content': resp.content
        }
        
        return cache_entry
    
    def cacheRelatedData(self, url: str, data: object):
        if url in self.__cache:
            if (data == None) and ('extra' in self.__cache['url']):
                del self.__cache[url]['extra']
            else:
                self.__cache[url]['extra'] = data
        else:
            raise ValueError(f'{url} is not in the cache')