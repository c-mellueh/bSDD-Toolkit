from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import bsdd
import bsdd_json
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import class_utils as class_utils
import argparse
from bsdd_json import (
    BsddClass,
    BsddDictionary,
    BsddClassProperty,
    BsddProperty,
    BsddClassRelation,
    BsddPropertyRelation,
)
import tqdm

client = bsdd.Client()


def swap_codes(data_dict, old, new):
    if old not in data_dict:
        return
    data_dict[new] = data_dict[old]
    data_dict.pop(old)


def import_dictionary(dictionary_uri):
    def read_lang_code():
        if "availableLanguages" not in dictionary_data:
            return
        dictionary_data.pop("availableLanguages")

    dictionary_data = client.get_dictionary(dictionary_uri)["dictionaries"][0]
    read_lang_code()
    swap_codes(dictionary_data, "organizationCodeOwner", "OrganizationCode")
    swap_codes(dictionary_data, "code", "DictionaryCode")
    swap_codes(dictionary_data, "version", "DictionaryVersion")
    swap_codes(dictionary_data, "defaultLanguageCode", "LanguageIsoCode")
    swap_codes(dictionary_data, "name", "DictionaryName")
    swap_codes(dictionary_data, "changeRequestEmail", "ChangeRequestEmailAddress")
    dictionary_data["LanguageOnly"] = False
    dictionary_data["UseOwnUri"] = False
    return BsddDictionary.model_validate(dictionary_data)


def get_all_classes(dictionary_uri: str, bsdd_dictionary: BsddDictionary):
    classes_info = list()
    class_count = 0
    total_count = None
    while total_count is None or class_count < total_count:
        cd = client.get_classes(
            dictionary_uri, use_nested_classes=False, limit=1_000, offset=class_count
        )
        classes_info += cd["classes"]
        class_count += cd["classesCount"]
        total_count = cd["classesTotalCount"]
    loaded_classes = list()

    for c in tqdm.tqdm(classes_info, "Load Classes"):
        loaded_classes.append(
            class_utils.load_class(c["uri"], bsdd_dictionary, True, True, client)
        )
    return loaded_classes


def get_all_properties(dictionary_uri):
    property_info = list()
    property_count = 0
    total_count = None
    while total_count is None or property_count < total_count:
        pd = client.get_properties(dictionary_uri, limit=1000, offset=property_count)
        property_info += pd["properties"]
        property_count += pd["propertiesCount"]
        total_count = pd["propertiesTotalCount"]

    loaded_properties = list()
    for p in tqdm.tqdm(property_info, "Load Properties"):
        loaded_properties.append(prop_utils.load_property(p["uri"], client=client))
    return loaded_properties


def main(bsdd_uri: str, save_path: str):
    bsdd_dictionary = import_dictionary(bsdd_uri)
    bsdd_dictionary.Classes = get_all_classes(bsdd_uri, bsdd_dictionary)
    bsdd_dictionary.Properties = get_all_properties(bsdd_uri)
    bsdd_dictionary.save(save_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download bSDD from URI")
    parser.add_argument(
        "bsdd_uri",
        type=str,
        help="example = https://identifier.buildingsmart.org/uri/hw/som/0.2.2",
    )
    parser.add_argument(
        "save_path", type=Path, help="Output Path to the BSDD JSON file"
    )
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_args()
    print(args)
    main(args.bsdd_uri, args.save_path)
