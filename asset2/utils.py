def ll2px(geo_pos, corners, px_size):

    lat_length = abs(corners[0]["lat"] - corners[2]["lat"]) # vertical
    lng_length = abs(corners[1]["lng"] - corners[0]["lng"]) # horizontal

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
    # Since time calculation only works on datetime (not time), so we first
    # combine self.time with today, then get the time() part
    from datetime import date, datetime, timedelta
    holder = datetime.combine(date.today(), t)
    return (holder + timedelta(seconds = dt)).time()

def new_hash():
    import uuid
    return uuid.uuid4().hex
