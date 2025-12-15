"""CLI to find bSDD properties whose names contain a substring and list their classes.

Usage:
    python find_properties_by_name.py <input_bsdd_json> <output_txt>
"""

import argparse
from pathlib import Path
from bsdd_json import BsddClassProperty, BsddDictionary

NAME = "typ"


def find_classes(bsdd_dictionary: BsddDictionary, bsdd_prop: BsddClassProperty):
    classes = []
    for bsdd_class in bsdd_dictionary.Classes:
        for bsdd_class_property in bsdd_class.ClassProperties:
            if bsdd_class_property.PropertyCode == bsdd_prop.Code:
                classes.append(bsdd_class)
    return classes


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find properties containing a name fragment and list their classes."
    )
    parser.add_argument(
        "input_path", help="Path to the bSDD JSON file to search for properties."
    )
    parser.add_argument(
        "output_path", help="Path to write the matching properties and class names."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    bsdd_dictionary = BsddDictionary.load(str(args.input_path))

    results = []
    for bsdd_property in bsdd_dictionary.Properties:
        prop_name = bsdd_property.Name
        if prop_name and NAME.lower() in prop_name.lower():
            classes = find_classes(bsdd_dictionary, bsdd_property)
            results.append(f"{prop_name} -> {', '.join([c.Name for c in classes])}")

    output_path = Path(args.output_path)
    output_path.write_text("\n".join(results), encoding="utf-8")


if __name__ == "__main__":
    main()
