#!/usr/bin/env python3
import sys
import numpy
import logging
from enum import Enum
from fastkml import kml

from utils import export_to_json, create_output_folder

OUTPUT_FOLDER = "./build/"
INPUT_KML = "./airport.kml"
BACKGROUND_IMAGE_SIZE = 960

# Setups logger
logger = logging.getLogger(__name__)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger_handler.setLevel(logging.DEBUG)
logger.addHandler(logger_handler)
logger.setLevel(logging.DEBUG)

class NameAssigner():

    name_pool = {}

    """
    We don't allow two objects with same name, so we rename the second or later
    occurrences.
    """
    def rename(self, name):
        if not name:
            name = "NULL"
        count = self.name_pool.get(name, 0)
        new_name = None
        if count > 0:
            new_name = name + "-seg-" + str(count)
        self.name_pool[name] = count + 1
        return new_name if new_name else name


node_name_assigner = NameAssigner()
link_name_assigner = NameAssigner()


class LayerType(Enum):
    gate = 0
    spot = 1
    runway_and_taxiway = 2
    pushback_way = 3
    airport = 4


def main():

    # Creates the output folder
    create_output_folder(OUTPUT_FOLDER)

    # Gets KML document from file
    kml_doc = get_kml_document()

    # Generates airport data
    logger.debug("Generating airport metadata")
    generate_airport_data(kml_doc)
    logger.debug("Airport metadata generated")

    # Generates gate data
    logger.debug("Generating gate data")
    generate_node_data(kml_doc, LayerType.gate, "gates.json")
    logger.debug("Gate data generated")

    # Generates spot position
    logger.debug("Generating spot position data")
    generate_node_data(kml_doc, LayerType.spot, "spots.json")
    logger.debug("Spot position data generated")

    # Generates runway data
    logger.debug("Genenrating runway data")
    generate_link_data(kml_doc, LayerType.runway_and_taxiway, "runways.json",
                       "runway", True)
    logger.debug("Runway data generated")

    # Generates taxiway data
    logger.debug("Genenrating taxiway data")
    generate_link_data(kml_doc, LayerType.runway_and_taxiway, "taxiways.json",
                       "taxiway", True)
    logger.debug("Taxiway data generated")

    # Generates pushback way data
    logger.debug("Genenrating pushback way data")
    generate_link_data(kml_doc, LayerType.pushback_way, "pushback_ways.json")
    logger.debug("Pushback way data generated")

    # Warning: Generates scenario
    logger.debug("Please generate scenario using generate_scenario.py")


def get_kml_document():

    k = kml.KML()
    with open(INPUT_KML, "rb") as f:
        k.from_string(f.read())
    return list(k.features())[0]


def get_layer(kml_doc, layer_type):
    folders = list(kml_doc.features())
    return folders[layer_type.value]


def generate_airport_data(kml_doc):

    generate_airport_metadata(kml_doc)
    generate_airport_background_image()


def generate_airport_metadata(kml_doc):

    layer = get_layer(kml_doc, LayerType.airport)
    placemark = list(layer.features())[0]
    bounds = placemark.geometry.bounds

    # Gets airport center
    center = {
        "lat": (bounds[1] + bounds[3]) / 2,
        "lng": (bounds[0] + bounds[2]) / 2
    }

    # Gets airport corners
    min_lat = min(bounds[1], bounds[3])
    max_lat = max(bounds[1], bounds[3])
    min_lng = min(bounds[0], bounds[2])
    max_lng = max(bounds[0], bounds[2])
    corners = [
        {"lat": max_lat, "lng": min_lng},
        {"lat": max_lat, "lng": max_lng},
        {"lat": min_lat, "lng": min_lng},
        {"lat": min_lat, "lng": max_lng},
    ]

    airport = {
        "name": kml_doc.name,
        "center": center,
        "corners": corners
    }

    # Export data to file
    filename = OUTPUT_FOLDER + "airport-metadata.json"
    export_to_json(filename, airport)


def generate_airport_background_image():

    # Generates the background image (plain white)
    filename = OUTPUT_FOLDER + "airport.jpg"

    from PIL import Image
    img = Image.new('RGB', (BACKGROUND_IMAGE_SIZE, BACKGROUND_IMAGE_SIZE),
                    (255, 255, 255))
    img.save(filename, "JPEG")


def generate_node_data(kml_doc, layer_type, output_filename):

    nodes = []

    layer = get_layer(kml_doc, layer_type)
    placemarks = list(layer.features())

    for p in placemarks:
        nodes.append({
            "name": node_name_assigner.rename(p.name),
            "lat": p.geometry.y,
            "lng": p.geometry.x
        })

    export_to_json(OUTPUT_FOLDER + output_filename, nodes)


def generate_link_data(kml_doc, layer_type, output_filename,
                       aeroway_filter = None, use_ref = False):

    links = []

    layer = get_layer(kml_doc, layer_type)
    placemarks = list(layer.features())

    for p in placemarks:

        if aeroway_filter and not is_aeroway_matched(p, aeroway_filter):
            continue

        if use_ref:
            p.name = get_ref(p)

        nodes = []
        for coord in p.geometry.coords:
            nodes.append(coord[0:2])
        links.append({
            "name": link_name_assigner.rename(p.name),
            "nodes": nodes
        })

    export_to_json(OUTPUT_FOLDER + output_filename, links)

def is_aeroway_matched(placemark, aeroway_filter):

    for i in placemark.extended_data.elements:
        if i.name == "aeroway" and i.value == aeroway_filter:
            return True

    return False

def get_ref(placemark):

    for i in placemark.extended_data.elements:
        if i.name == "ref" and i.value is not None and len(i.value) != 0:
            return i.value

    return placemark.name


if __name__ == "__main__":
    main()
