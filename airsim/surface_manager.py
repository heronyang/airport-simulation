import os
import csv
import json

from airport import Airport
from gate import Gate
from surface import Surface

class SurfaceManager:

    DATA_ROOT_DIR_PATH = "./data/"
    FILES_TO_CHECK = [
        "airport-metadata.json",
        "airport.jpg",
        "gates.csv"
    ]

    airport_code = None
    dir_path = None
    surface = Surface()

    def __init__(self, iata_airport_code):

        # Checks if the airport folder/files are ready
        self.dir_path = self.DATA_ROOT_DIR_PATH + iata_airport_code + "/"
        if not self.__is_data_ready():
            raise Exception("Airport %s data is not ready" % iata_airport_code)

        self.airport_code = iata_airport_code
        self.__load_airport()
        self.__load_gates()

    def __is_data_ready(self):

        # Checks if the folder exists
        if not os.path.exists(self.dir_path):
            return False

        # Checks if the files exist
        for f in self.FILES_TO_CHECK:
            file_path = self.dir_path + f
            if not os.path.exists(file_path):
                return False

        return True

    def __load_airport(self):
        with open(self.dir_path + "airport-metadata.json") as f:
            airport_md = json.load(f)
            self.surface.airport = Airport(
                airport_md["name"], airport_md["center"],
                airport_md["corners"], self.DATA_ROOT_DIR_PATH +
                self.airport_code+ "/airport.jpg")

    def __load_gates(self):

        with open(self.dir_path + "gates.csv") as f:
            reader = csv.reader(f, delimiter = ",")
            next(reader)
            for row in reader:
                index, name, lat, lng = row[0], row[1], float(row[2]), float(row[3])
                self.surface.gates.append(Gate(index, name,
                                               {"lat": lat, "lng": lng}))
