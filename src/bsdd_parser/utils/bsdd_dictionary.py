from urllib.parse import urlparse


def get_dictionary_path_from_uri(uri: str) -> str:
    """
    Parse a buildingSMART identifier URI of the form:
    https://identifier.buildingsmart.org/uri/<company>/<library>/<version>/

    Returns the base URI up to the version, or an empty string if invalid.
    """
    base_prefix = "https://identifier.buildingsmart.org/uri/"

    # Ensure URI starts with required prefix
    if not uri.startswith(base_prefix):
        return ""

    parsed = urlparse(uri)
    path_parts = parsed.path.strip("/").split("/")

    # Path must contain at least company, library, version
    if len(path_parts) < 4:
        return ""

    # Construct normalized result
    result = f"{base_prefix}{path_parts[1]}/{path_parts[2]}/{path_parts[3]}/"
    return result
