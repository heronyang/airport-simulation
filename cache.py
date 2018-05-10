"""`Cache` offers put/get inferface for a simple key-value store on disk."""
import os
import pickle
import logging

CACHE_DIR = "./cache/"
LOGGER = logging.getLogger(__name__)


def put(key, obj):
    """Puts a key value pair into the store."""
    LOGGER.debug("Putting a new cache with key %s", key)
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with open(CACHE_DIR + key + ".pkl", 'wb') as fout:
        pickle.dump(obj, fout, pickle.HIGHEST_PROTOCOL)


def get(key):
    """Gets the value stored using the given key."""
    LOGGER.debug("Getting a cache with key %s", key)
    try:
        with open(CACHE_DIR + key + ".pkl", 'rb') as fout:
            return pickle.load(fout)
    except FileNotFoundError:
        LOGGER.debug("No cache file found")
        return None


def get_hash(links, nodes):
    """Gets the hash value of the given links and nodes."""

    import hashlib

    __hash = 0.0
    for link in links:
        __hash += link.__hash__()
        __hash += link.__hash__()

    for node in nodes:
        __hash += node.__hash__()
        __hash += node.__hash__()

    return hashlib.md5(('%d' % __hash).encode('utf-8')).hexdigest()
