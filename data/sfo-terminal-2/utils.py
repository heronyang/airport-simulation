import os
import json


def export_to_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def create_output_folder(folder_name):
    try:
        os.makedirs(folder_name)
    except OSError as e:
        pass
