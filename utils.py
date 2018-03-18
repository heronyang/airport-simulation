def ll2px(geo_pos, corners, px_size):

    lat_length = abs(corners[0]["lat"] - corners[2]["lat"])  # vertical
    lng_length = abs(corners[1]["lng"] - corners[0]["lng"])  # horizontal

    orin_top = abs(geo_pos["lat"] - corners[0]["lat"])
    orin_left = abs(geo_pos["lng"] - corners[0]["lng"])

    pix_top = int(px_size * (orin_top / lat_length))
    pix_left = int(px_size * (orin_left / lng_length))

    return px_bound(pix_left, px_size), px_bound(pix_top, px_size)


def px_bound(px, size):
    return max(min(px, size), 0)


def str2time(s):

    from datetime import time
    hours = int(s[0:2])
    mins = int(s[2:4])

    return time(hours, mins)


def is_valid_geo_pos(geo_pos):
    lat = geo_pos["lat"]
    lng = geo_pos["lng"]
    if lat < -90 or lat > 90:
        return False
    if lng < -180 or lng > 180:
        return False
    return True


def get_seconds_after(t, dt):
    """
    Since time calculation only works on datetime (not time), so we first
    combine self.time with today, then get the time() part. Note that if
    overflow occurs, the output will be earlier
    """
    from datetime import date, datetime, timedelta
    holder = datetime.combine(date.today(), t)
    res = (holder + timedelta(seconds=dt)).time()
    return res


def get_seconds_before(t, dt):
    from datetime import date, datetime, timedelta
    holder = datetime.combine(date.today(), t)
    res = (holder - timedelta(seconds=dt)).time()
    return res


def get_seconds_taken(src, dst, velocity):
    import math
    distance = src.get_distance_to(dst)
    return int(math.ceil(distance / velocity))


def str2sha1(s):
    import hashlib
    return int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16)


def interpolate_geo(start, end, ratio):
    """
    Interpolation method
    """
    s_geo = start.geo_pos
    e_geo = end.geo_pos
    lat = s_geo["lat"] + (e_geo["lat"] - s_geo["lat"]) * ratio
    lng = s_geo["lng"] + (e_geo["lng"] - s_geo["lng"]) * ratio
    return {"lat": lat, "lng": lng}


def get_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second


def get_time_delta(t1, t2):
    m1 = t1.hour * 60 * 60 + t1.minute * 60 + t1.second
    m2 = t2.hour * 60 * 60 + t2.minute * 60 + t2.second
    return m1 - m2

def random_string(length):
    import string
    import random
    return ''.join(random.choice(string.ascii_letters) for m in range(length))

def update_dict(ori_dict, new_dict):
    import collections
    for key, value in new_dict.items():
        ori_dict[key] = update_dict(ori_dict.get(key, {}), value) \
                if isinstance(value, collections.Mapping) else value
    return ori_dict
