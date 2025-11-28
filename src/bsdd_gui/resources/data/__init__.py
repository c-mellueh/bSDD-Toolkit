import os
import json

DATA_PATH = os.path.dirname(__file__)


def get_ifc_classes() -> dict:
    path = os.path.join(DATA_PATH, "ifc_classes.json")
    with open(path, "r") as file:
        return json.load(file)

def get_ifc_type_classes() -> dict:
    path = os.path.join(DATA_PATH, "ifc_type_classes.json")
    with open(path, "r") as file:
        return json.load(file)
