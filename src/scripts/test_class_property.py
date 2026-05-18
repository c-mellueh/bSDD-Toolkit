import marimo

__generated_with = "0.17.6"
app = marimo.App(width="full")


@app.cell
def _():
    import bsdd
    from bsdd_json.utils import class_utils as class_utils
    from bsdd_json import BsddDictionary
    client = bsdd.Client()

    def swap_codes(data_dict,old,new):
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
        swap_codes(dictionary_data,"organizationCodeOwner","OrganizationCode")
        swap_codes(dictionary_data,"code","DictionaryCode")
        swap_codes(dictionary_data,"version","DictionaryVersion")
        swap_codes(dictionary_data,"defaultLanguageCode","LanguageIsoCode")
        swap_codes(dictionary_data,"name","DictionaryName")
        swap_codes(dictionary_data,"changeRequestEmail","ChangeRequestEmailAddress")
        dictionary_data["LanguageOnly"] = False
        dictionary_data["UseOwnUri"] = False
        return BsddDictionary.model_validate(dictionary_data)

    def import_existing_dictionary(release_date):
        old_dict = BsddDictionary.load(r"C:\Users\melluehc\Desktop\som-0.2.2.json")
        old_dict.Status = "Active"
        old_dict.ReleaseDate = release_date
        old_dict.DictionaryUri = None
        return old_dict

    dictionary_uri = "https://identifier.buildingsmart.org/uri/etim/etim/10.1"
    save_path = "test.json"

    bsdd_dictionary = import_dictionary(dictionary_uri)

    return client, dictionary_uri


@app.cell
def _():


    return


@app.cell
def _(client, dictionary_uri):
    classes_info = list() 
    class_count = 0
    total_count = 1_000_000
    while class_count < total_count:
        cd = client.get_classes(dictionary_uri,use_nested_classes=False,limit=1_000,offset=class_count)
        classes_info+=cd["classes"]
        class_count+=cd["classesCount"]
        total_count = cd["classesTotalCount"]
        print(class_count)
    return cd, classes_info


@app.cell
def _(cd):
    cd
    return


@app.cell
def _(classes_info):
    classes_info
    return


if __name__ == "__main__":
    app.run()
