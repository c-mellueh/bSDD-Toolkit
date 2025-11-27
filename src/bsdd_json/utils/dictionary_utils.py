from urllib.parse import urlparse, quote
import re
import unicodedata

def slugify(text: str, *, delimiter: str = "-", lowercase: bool = False, max_length: int | None = None) -> str:
    """
    Convert a string into a URL-friendly slug.

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
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
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
    slug = re.sub(fr"{re.escape(delimiter)}+", delimiter, slug).strip(delimiter)

    # 5) Casing
    if lowercase:
        slug = slug.lower()

    # 6) Optional length limit (avoid trailing delimiter after cut)
    if max_length is not None and max_length > 0 and len(slug) > max_length:
        slug = slug[:max_length].rstrip(delimiter)

    return slug


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


def is_uri(s: str) -> bool:
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])  # requires scheme + host
    except ValueError:
        return False


def parse_bsdd_url(url: str) -> dict:
    from urllib.parse import urlparse

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
        "after_uri": after,
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


def build_bsdd_url(data: dict, trailing_slash: bool = False) -> str:
    """
    Build a buildingSMART identifier URI from a dict produced by parse_bsdd_url
    or from a dict with keys:
    - scheme (default "https")
    - host (default "identifier.buildingsmart.org")
    - after_uri
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
        #Disable quoting for bsDD URIs
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

    if ns_parts and version and rtype and rid:
        after = [*ns_parts, str(version), str(rtype), str(rid)]
        parts = ["uri", *after]
        path = "/" + "/".join(q(p) for p in parts)
    else:
        # 2) Otherwise, use `after_uri` if available
        after = data.get("after_uri")
        if after:
            parts = ["uri", *[str(p) for p in after if str(p)]]
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
                    parts = [
                        str(p).strip("/") for p in path_segments if str(p).strip("/")
                    ]
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
    else:
        if url.endswith("/"):
            url = url[:-1]

    return url
