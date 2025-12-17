"""CLI script to export classes and properties missing definitions to an Excel file.

Usage:
    python list_empty_definitions.py <input_bsdd_json> <output_xlsx>
"""

import argparse
from pathlib import Path
import json
import openpyxl
from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import class_utils as class_utils
from bsdd_json.utils import property_utils as prop_utils


def find_property(bsdd_class: BsddClass, property_name: str):
    for bsdd_class_property in bsdd_class.ClassProperties:
        if property_name == prop_utils.get_name(
            bsdd_class_property, bsdd_class.parent()
        ):
            return bsdd_class_property
    return None


def read_excel(excel_path, input_dict_path, ouput_dict_path):
    bsdd_dict = BsddDictionary.load(input_dict_path)
    excel = openpyxl.open(excel_path)
    name_dict = {c.Name: c for c in bsdd_dict.Classes}
    for row in excel.active:
        class_name = row[0].value
        property_name = row[1].value
        description = row[3].value
        bsdd_class = name_dict.get(class_name)

        if not bsdd_class:
            continue
        bsdd_class_property = find_property(bsdd_class, property_name)
        if not bsdd_class_property:
            continue
        bsdd_class_property.Description = description
    bsdd_dict.save(ouput_dict_path)

def read_json(json_path, input_dict_path, ouput_dict_path):
    bsdd_dict = BsddDictionary.load(input_dict_path)
    with open(json_path,"r") as file:
        data = json.load(file)

    name_dict = {c.Name: c for c in bsdd_dict.Classes}
    for class_name,property_dict in data.items():
        bsdd_class = name_dict.get(class_name)
        if not bsdd_class:
            continue 

        for property_name,description in property_dict.items():
            bsdd_class_property = find_property(bsdd_class, property_name)
            if not bsdd_class_property:
                continue
            bsdd_class_property.Description = description
    bsdd_dict.save(ouput_dict_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List BSDD classes and properties without definitions into an Excel file."
    )
    parser.add_argument("mode", type=str, help="'excel' or 'json'")

    parser.add_argument("input_file", type=Path, help="Path to the input_file")
    parser.add_argument(
        "bsdd_input", type=Path, help="Input Path to the BSDD JSON file"
    )
    parser.add_argument(
        "bsdd_output", type=Path, help="Output Path to the BSDD JSON file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.mode == "json":
        read_json(args.input_file,args.bsdd_input,args.bsdd_output)
    elif args.mode == "excel":
        read_excel(args.input_file,args.bsdd_input,args.bsdd_output)
    else:
        print(f"mode '{args.mode}' not found")
