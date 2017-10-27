import os
import pickle
import logging

CACHE_DIR = "./cache/"
logger = logging.getLogger(__name__)

def put(key, obj):
    logger.debug("Putting a new cache with key %s" % key)
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with open(CACHE_DIR + key + ".pkl", 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def get(key):
    logger.debug("Getting a cache with key %s" % key)
    try:
        with open(CACHE_DIR + key + ".pkl", 'rb') as f:
            return pickle.load(f)
    except Exception:
        # Cache file does not exist
        logger.debug("No cache file found")
        return None

def hash(links, nodes):

    import hashlib

    f = 0.0
    for link in links:
        f += link.start.geo_pos["lat"]
        f += link.start.geo_pos["lng"]

    for node in nodes:
        f += node.geo_pos["lat"]
        f += node.geo_pos["lng"]

    return hashlib.md5(('%.10f' % f).encode('utf-8')).hexdigest()
