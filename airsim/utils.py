def ll2px(geo_pos, corners, px_size):

    lat_length = abs(corners[0]["lat"] - corners[2]["lat"]) # vertical
    lng_length = abs(corners[1]["lng"] - corners[0]["lng"]) # horizontal

    orin_top = abs(geo_pos["lat"] - corners[0]["lat"])
    orin_left = abs(geo_pos["lng"] - corners[0]["lng"])

    pix_top = int(px_size * (orin_top / lat_length))
    pix_left = int(px_size * (orin_left / lng_length))

    return pix_left, pix_top
