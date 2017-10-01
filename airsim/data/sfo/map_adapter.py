import os
import requests
import urllib.parse

from gmerc import ll2px, px2ll

"""size = 640x640 with scale = 2 is the largest image supported as a free
Google API user
"""
SIZE = 640
SCALE = 2
ZOOM_LEVEL = 15
MAP_TYPE = "terrain"
STYLE_VISIBILITY = "feature:all|element:labels|visibility:off"
STYLE_COLOR = "feature:transit.station.airport|lightness:-12|saturation:100" \
        "|gamma:10.0|hue:0xFFAA33"

class MapAdapter:

    def download(self, filename, center):
        """Downloads map image to file with a sepcific center
        """

        if not "GOOGLE_MAP_API_KEY" in os.environ:
            raise Exception("GOOGLE_MAP_API_KEY as an environment variable " \
                            "is required for downloading static map image, " \
                            "get it at https://developers.google.com/maps/" \
                            "documentation/static-maps/get-api-key")
        
        api_key = os.environ["GOOGLE_MAP_API_KEY"]
        encoded_center = urllib.parse.quote(str(center["lat"]) + ", " +
                                            str(center["lng"]))
        url = "https://maps.googleapis.com/maps/api/staticmap" \
                "?center=%s&size=%s&zoom=%d&scale=%d&maptype=%s" \
                "&style=%s&style=%skey=%s" \
                % (encoded_center, str(SIZE) + "x" + str(SIZE), ZOOM_LEVEL,
                   SCALE, MAP_TYPE, STYLE_VISIBILITY, STYLE_COLOR, api_key)

        with open(filename, "wb") as f:
            f.write(requests.get(url).content)
        print("Map image downloaded at " + filename)

    def center2corners(self, center):
        """Gets the lat/lng value of four corners of the image file
        """

        center_px = ll2px(center["lat"], center["lng"], ZOOM_LEVEL)
        west_north_corner = px2ll(center_px[0] - SIZE/2,
                                  center_px[1] - SIZE/2, ZOOM_LEVEL)
        east_north_corner = px2ll(center_px[0] + SIZE/2,
                                  center_px[1] - SIZE/2, ZOOM_LEVEL)
        west_south_corner = px2ll(center_px[0] - SIZE/2,
                                  center_px[1] + SIZE/2, ZOOM_LEVEL)
        east_south_corner = px2ll(center_px[0] + SIZE/2,
                                  center_px[1] + SIZE/2, ZOOM_LEVEL)
        return [
            { "lat": west_north_corner[0], "lng": west_north_corner[1] },
            { "lat": east_north_corner[0], "lng": east_north_corner[1] },
            { "lat": west_south_corner[0], "lng": west_south_corner[1] },
            { "lat": east_south_corner[0], "lng": east_south_corner[1] }
        ]
