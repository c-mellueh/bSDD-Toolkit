"""CLI script to export classes and properties missing definitions to an Excel file.

Usage:
    python list_empty_definitions.py <input_bsdd_json> <output_xlsx>
"""

import argparse
from pathlib import Path

import openpyxl
from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
from bsdd_json.utils import property_utils as prop_utils


def list_empty_definitions(input_path: Path, output_path: Path) -> None:
    """Write classes/properties without definitions to an Excel workbook."""
    bsdd_dictionary = BsddDictionary.load(str(input_path))

    excel = openpyxl.Workbook()
    sheet = excel.active
    empty_classes: list[BsddClass] = []
    empty_properties: list[BsddClassProperty] = []

    for bsdd_class in bsdd_dictionary.Classes:
        if not bsdd_class.Definition:
            empty_classes.append(bsdd_class)

        for bsdd_class_property in bsdd_class.ClassProperties:
            if not bsdd_class_property.Description:
                bsdd_property = prop_utils.get_property_by_class_property(
                    bsdd_class_property, bsdd_dictionary
                )
                if not bsdd_property or not bsdd_property.Definition:
                    empty_properties.append(bsdd_class_property)

    sheet.title = "Classes"
    for bsdd_class in empty_classes:
        sheet.append(
            [bsdd_class.Code, bsdd_class.Name, "; ".join(bsdd_class.RelatedIfcEntityNamesList)]
        )

    property_sheet = excel.create_sheet("Properties")
    for bsdd_class_property in sorted(empty_properties, key=lambda p: p.Code):
        bsdd_class = bsdd_class_property.parent()
        name = prop_utils.get_name(bsdd_class_property)
        property_sheet.append(
            [bsdd_class.Name, name, "; ".join([x.Value for x in bsdd_class_property.AllowedValues])]
        )

    excel.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List BSDD classes and properties without definitions into an Excel file."
    )
    parser.add_argument("input_path", type=Path, help="Path to the BSDD JSON file")
    parser.add_argument("output_path", type=Path, help="Path where the Excel file will be written")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    list_empty_definitions(args.input_path, args.output_path)
