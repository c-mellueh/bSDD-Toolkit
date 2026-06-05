from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING, TypedDict
from urllib.parse import quote, urlparse

if TYPE_CHECKING:
    from bsdd_json.models import BsddDictionary

BASE_PREFIX = "https://identifier.buildingsmart.org/uri/"


class UriDict(TypedDict):
    """Structured representation of a parsed buildingSMART identifier URI.

    Produced by :func:`parse_bsdd_url` and consumed by :func:`build_bsdd_url`.

    Attributes
    ----------
    scheme : str
        URL scheme, e.g. ``"https"``.
    host : str
        Hostname, e.g. ``"identifier.buildingsmart.org"``.
    path_segments : list[str]
        All non-empty path segments of the URL, without leading/trailing slashes.
    namespace : str | None
        Organization and dictionary code joined by ``/``, e.g. ``"hw/som"``.
        ``None`` when it could not be determined.
    version : str | None
        Dictionary version string, e.g. ``"0.2.0"``.  ``None`` when unknown.
    resource_type : str | None
        Resource kind, e.g. ``"class"`` or ``"property"``.  ``None`` when unknown.
    resource_id : str | None
        Identifier of the specific resource, e.g. ``"Leiter"``.  ``None`` when unknown.

    """

    scheme: str
    host: str
    path_segments: list[str]
    namespace: str | None
    version: str | None
    resource_type: str | None
    resource_id: str | None


def slugify(text: str, *, delimiter: str = "-", lowercase: bool = False, max_length: int | None = None) -> str:
    """Convert a string into a URL-friendly slug.

    - Transliterate German umlauts/ß: ä→ae, ö→oe, ü→ue, Ä→Ae, Ö→Oe, Ü→Ue, ß→ss
    - Strip accents/diacritics (é → e, å → a, etc.)
    - Replace any run of non-alphanumeric characters with `delimiter`
    - Collapse repeated delimiters and trim from ends
    - Optionally lowercase and/or truncate to `max_length`

    Parameters
    ----------
    text : str
        Input string (any language).
    delimiter : str, default "-"
        Character to use as word separator.
    lowercase : bool, default True
        Whether to lowercase the output.
    max_length : int | None, default None
        If set, truncate the slug to this length (without cutting in the middle
        of a delimiter run when possible).

    Returns
    -------
    str
        URL-safe slug (ASCII only).

    """
    if not isinstance(text, str):
        text = str(text)

    # 1) German-specific replacements first (before accent stripping)
    german_map = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
    }
    text = "".join(german_map.get(ch, ch) for ch in text)

    # 2) Strip accents/diacritics -> ASCII
    # Normalize to NFKD and drop combining marks
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))
    # Keep only ASCII
    ascii_text = ascii_text.encode("ascii", "ignore").decode("ascii")

    # 3) Replace non-alphanumeric with delimiter
    # Allow a-z, A-Z, 0-9. Everything else -> delimiter
    slug = re.sub(r"[^A-Za-z0-9]+", delimiter, ascii_text)

    # 4) Collapse repeats and trim delimiters from ends
    slug = re.sub(rf"{re.escape(delimiter)}+", delimiter, slug).strip(delimiter)

    # 5) Casing
    if lowercase:
        slug = slug.lower()

    # 6) Optional length limit (avoid trailing delimiter after cut)
    if max_length is not None and max_length > 0 and len(slug) > max_length:
        slug = slug[:max_length].rstrip(delimiter)

    return slug


def get_dictionary_path_from_uri(uri: str) -> str:
    """Parse a buildingSMART identifier URI of the form: https://identifier.buildingsmart.org/uri/<company>/<library>/<version>/.

    Returns the base URI up to the version, or an empty string if invalid.
    """
    min_path_length = 4
    # Ensure URI starts with required prefix
    if not uri.startswith(BASE_PREFIX):
        return ""

    parsed = urlparse(uri)
    path_parts = parsed.path.strip("/").split("/")

    # Path must contain at least company, library, version
    if len(path_parts) < min_path_length:
        return ""

    # Construct normalized result
    return f"{BASE_PREFIX}{path_parts[1]}/{path_parts[2]}/{path_parts[3]}/"


def normalize_uri(uri: str | None) -> str | None:
    """Return a casing-normalized form of *uri* for use as a lookup/dict key.

    bSDD URIs may be stored with differing casing in different places (e.g. a
    ``RelatedClassUri`` copied from another source vs. one built locally). Using
    the raw value as a dictionary key therefore causes lookups to miss. This
    helper lowercases the URI so all comparisons happen on a common form.

    ``None`` is passed through unchanged so callers can normalize optional URIs
    without extra guarding.
    """
    if uri is None:
        return None
    return str(uri).lower()


def is_uri(s: str) -> bool:
    """Return True if the string looks like an absolute URI with scheme and host.

    The check is intentionally lightweight: it parses the string with
    ``urllib.parse.urlparse`` and returns True only when both ``scheme`` and
    ``netloc`` are present (for example ``https://example.com/x``). Bare codes,
    relative paths, or malformed inputs return False.
    """
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])  # requires scheme + host
    except ValueError:
        return False


def parse_bsdd_url(url: str) -> UriDict:
    """Parse a buildingSMART identifier URL into its constituent parts.

    Splits the URL into scheme, host, and path segments, then attempts to
    locate the ``uri`` marker in the path to extract the namespace, version,
    resource type, and resource ID.

    Expected canonical layout after the ``uri`` marker:
    ``<org>/<code>/<version>/<resource_type>/<resource_id>``

    For shorter paths a best-effort extraction is performed.
    """
    p = urlparse(url)
    path_parts = [p for p in p.path.strip("/").split("/") if p]

    # try to find the "uri" marker and the meaningful parts after it
    if "uri" in path_parts:
        i = path_parts.index("uri")
        after = path_parts[i + 1 :]
    else:
        after = path_parts

    result = {
        "scheme": p.scheme,
        "host": p.netloc,
        "path_segments": path_parts,
        "namespace": None,
        "version": None,
        "resource_type": None,
        "resource_id": None,
    }

    # expected layout (common): hw / som / 0.2.0 / class / Leiter
    if len(after) >= 5:
        result["namespace"] = "/".join(after[0:2])  # "hw/som"
        result["version"] = after[2]  # "0.2.0"
        result["resource_type"] = after[3]  # "class"
        result["resource_id"] = after[4]  # "Leiter"
    else:
        # best-effort fill for other shapes
        if len(after) >= 1:
            result["resource_type"] = after[-2] if len(after) >= 2 else None
            result["resource_id"] = after[-1]
        if len(after) >= 3:
            result["version"] = after[-3]

    return result


def bsdd_dictionary_url(bsdd_dictionary: BsddDictionary) -> str:
    """Build the canonical dictionary-level URI for a ``BsddDictionary``.

    Delegates to :func:`build_bsdd_url` after assembling a data dict from the
    dictionary's ``OrganizationCode``, ``DictionaryCode``, ``DictionaryVersion``,
    and (when ``UseOwnUri`` is set) ``DictionaryUri``.  The returned URL always
    has a trailing slash.

    Parameters
    ----------
    bsdd_dictionary : BsddDictionary
        The dictionary model instance to generate the URI for.

    Returns
    -------
    str
        Trailing-slash URI such as
        ``https://identifier.buildingsmart.org/uri/hw/som/0.2.0/dictionary/``,
        or an empty string if required fields are missing.

    """
    data = {
        "namespace": [bsdd_dictionary.OrganizationCode, bsdd_dictionary.DictionaryCode],
        "version": bsdd_dictionary.DictionaryVersion,
        "resource_type": "dictionary",
        "resource_id": "",
    }
    if bsdd_dictionary.UseOwnUri:
        data["host"] = bsdd_dictionary.DictionaryUri

    return build_bsdd_url(data, trailing_slash=True)


def build_bsdd_url(data: UriDict, trailing_slash: bool = False) -> str:
    """Build a buildingSMART identifier URI from a dict produced by parse_bsdd_url
    or from a dict with keys:
    - scheme (default "https")
    - host (default "identifier.buildingsmart.org")
    - namespace: "hw/som" or ["hw","som"]
    - version
    - resource_type
    - resource_id
    - path_segments: full list of segments (may include leading "uri")
    Returns constructed URI string or empty string if not enough information.

    """
    scheme = data.get("scheme", "https")
    host = data.get("host", "identifier.buildingsmart.org")

    # Validate base parts
    if not scheme or not host:
        return ""

    # Helper to quote path segments fast
    def q(seg: str) -> str:
        return seg
        # Disable quoting for bsDD URIs
        return quote(str(seg), safe="")

    # 1) Build canonical bsDD shape if sufficient fields are present
    ns = data.get("namespace")
    if isinstance(ns, (list, tuple)):
        ns_parts = [str(s) for s in ns if str(s)]
    elif isinstance(ns, str) and ns:
        ns_parts = [p for p in ns.strip("/").split("/") if p]
    else:
        ns_parts = []

    version = data.get("version")
    rtype = data.get("resource_type")
    rid = data.get("resource_id")

    if rtype == "dictionary" and ns_parts and version:
        after = [*ns_parts, str(version)]
        parts = ["uri", *after]
        path = "/" + "/".join(q(p) for p in parts)
    elif ns_parts and version and rtype and rid:
        after = [*ns_parts, str(version), str(rtype), str(rid)]
        parts = ["uri", *after]
        path = "/" + "/".join(q(p) for p in parts)
    else:
        parts = data.get("path_segments")
        if parts:
            parts = [str(p) for p in parts if str(p)]
            if not parts:
                return ""
            path = "/" + "/".join(q(p) for p in parts)
        else:
            # 3) Fallback to explicit full path segments
            path_segments = data.get("path_segments")
            if path_segments:
                if isinstance(path_segments, str):
                    parts = [p for p in path_segments.strip("/").split("/") if p]
                else:
                    parts = [str(p).strip("/") for p in path_segments if str(p).strip("/")]
                if not parts:
                    return ""
                path = "/" + "/".join(q(p) for p in parts)
            else:
                return ""

    # Build final URL
    url = f"{scheme}://{host}{path}"
    if trailing_slash:
        if not url.endswith("/"):
            url += "/"
    elif url.endswith("/"):
        url = url[:-1]

    return url


def is_external_ref(uri: str, bsdd_dictionary: BsddDictionary) -> bool:
    """Return True if *uri* belongs to a different dictionary than *bsdd_dictionary*.

    Extracts the dictionary path from *uri* using
    :func:`get_dictionary_path_from_uri` and compares it against the canonical
    URI of *bsdd_dictionary*.  Empty or unparseable URIs are treated as
    non-external and return ``False``.

    Parameters
    ----------
    uri : str
        The URI to check.
    bsdd_dictionary : BsddDictionary
        The dictionary to compare against.

    Returns
    -------
    bool
        ``True`` if *uri* resolves to a different dictionary, ``False``
        otherwise (including when *uri* is empty or malformed).

    """
    if not uri:
        return False
    from .dictionary_utils import bsdd_dictionary_url, get_dictionary_path_from_uri

    dict_path = get_dictionary_path_from_uri(uri)
    return dict_path.lower() != str(bsdd_dictionary_url(bsdd_dictionary)).lower()


def is_ifc_reference(uri: str) -> bool:
    """Return True if *uri* points to the buildingSMART IFC dictionary.

    Checks for the fixed path segment ``/uri/buildingsmart/ifc/`` anywhere
    in the URI string.

    Parameters
    ----------
    uri : str
        The URI to inspect.

    Returns
    -------
    bool
        ``True`` when *uri* is an IFC reference, ``False`` otherwise.

    """
    return "/uri/buildingsmart/ifc/" in uri.lower()
