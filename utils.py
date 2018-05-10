"""A collection of global helper functions."""


def str2time(time_str):
    """Converts a string containing time information into a time object."""

    from datetime import time
    hours = int(time_str[0:2])
    mins = int(time_str[2:4])

    return time(hours, mins)


def is_valid_geo_pos(geo_pos):
    """Returns true if the given geo position is valid."""
    lat = geo_pos["lat"]
    lng = geo_pos["lng"]
    if lat < -90 or lat > 90:
        return False
    if lng < -180 or lng > 180:
        return False
    return True


def get_seconds_after(time, delta_time):
    """Since time calculation only works on datetime (not time), so we first
    combine self.time with today, then get the time() part. Note that if
    overflow occurs, the output will be earlier
    """
    from datetime import date, datetime, timedelta
    holder = datetime.combine(date.today(), time)
    res = (holder + timedelta(seconds=delta_time)).time()
    return res


def get_seconds_before(time, delta_time):
    """Gets `delta_time` before the given `time`."""
    from datetime import date, datetime, timedelta
    holder = datetime.combine(date.today(), time)
    res = (holder - timedelta(seconds=delta_time)).time()
    return res


def str2sha1(data):
    """Returns the SHA-1 hash value of a given string data."""
    import hashlib
    return int(hashlib.sha1(data.encode('utf-8')).hexdigest(), 16)


def get_seconds(time):
    """Gets the total seconds in a time object."""
    return (time.hour * 60 + time.minute) * 60 + time.second


def get_time_delta(from_time, to_time):
    """Returns the time gap between `from_time` and `to_time` in seconds."""
    return to_time.hour * 60 * 60 + to_time.minute * 60 + to_time.second -\
        from_time.hour * 60 * 60 + from_time.minute * 60 + from_time.second


def random_string(length):
    """Gets a random string with a fixed length."""
    import string
    import random
    return ''.join(random.choice(string.ascii_letters) for m in range(length))


def update_dict(ori_dict, new_dict):
    """Updates a diction `ori_dict` with the key/value from another dictionary,
    `new_dict`.
    """
    import collections
    for key, value in new_dict.items():
        ori_dict[key] = update_dict(ori_dict.get(key, {}), value) \
                if isinstance(value, collections.Mapping) else value
    return ori_dict


def get_output_dir_name():
    """Gets the name of the output directory of this simulation run. The folder
    is created automatically if it doesnt'n exist.
    """
    import os
    from config import Config
    dir_name = "%s%s/" % (Config.OUTPUT_DIR, Config.params["name"])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name


def get_batch_plan_name(original_name, expr_var, nth):
    """Gets the name of this simulation run given the batch plan name,
    experimental value name, and the nth time.
    """
    if nth is None:
        return original_name + "-batch-" + str(expr_var)
    return original_name + "-" + str(nth) + "-batch-" + str(expr_var)


def is_collinear(n1, n2, n3):
    """Returns true if this thress nodes are on the same line."""
    # If the area size is near 0, then the points are on the same line
    x1, y1 = n1.geo_pos["lat"], n1.geo_pos["lng"]
    x2, y2 = n2.geo_pos["lat"], n2.geo_pos["lng"]
    x3, y3 = n3.geo_pos["lat"], n3.geo_pos["lng"]
    area = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
    return area <= 1e-12
