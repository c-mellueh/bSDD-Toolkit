"""CLI script to remove bSDD properties that are not referenced by any class.

Usage:
    python delete_properties_with_no_classprop.py <input_bsdd_json> <output_bsdd_json>
"""

from __future__ import annotations

import argparse
from pathlib import Path

from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary


def find_classes(bsdd_dictionary: BsddDictionary, bsdd_prop: BsddClassProperty):
    classes = []
    for bsdd_class in bsdd_dictionary.Classes:
        for bsdd_class_property in bsdd_class.ClassProperties:
            if bsdd_class_property.PropertyCode == bsdd_prop.Code:
                classes.append(bsdd_class)
    return classes


def remove_unreferenced_properties(bsdd_dictionary: BsddDictionary):
    removed = []
    # Copy the list to avoid mutating while iterating
    for bsdd_property in list(bsdd_dictionary.Properties):
        classes = find_classes(bsdd_dictionary, bsdd_property)
        if classes:
            continue
        removed.append(bsdd_property.Name)
        bsdd_dictionary.Properties.remove(bsdd_property)
    return removed


def main(input_path: Path, output_path: Path):
    bsdd_dictionary = BsddDictionary.load(str(input_path))
    removed_names = remove_unreferenced_properties(bsdd_dictionary)
    for name in removed_names:
        print(f"Remove {name}")
    bsdd_dictionary.save(str(output_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove properties that are not referenced by any class."
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to the input bsdd JSON file.",
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help="Path to write the cleaned bsdd JSON file.",
    )
    args = parser.parse_args()

    main(args.input_path, args.output_path)
