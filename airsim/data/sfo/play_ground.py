#!/usr/bin/env python

import json
from IPython.core.debugger import Tracer

with open("surface.json") as f:    
    surface_data = json.load(f)
    features = surface_data["features"]

    # Shows all type of aeroways
    aeroways = set()
    for feature in features:
        aeroways.add(feature["properties"]["aeroway"])
    print(aeroways)
    Tracer()()
