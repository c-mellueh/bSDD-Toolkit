from typing import TypedDict, Literal
from bsdd_json import BsddClass, BsddProperty

JSON_MIME = "application/bsdd-class+json;v=1"
CODES_MIME = "application/x-bsdd-classcode"  # for fast internal moves


class PAYLOAD(TypedDict):
    kind: Literal["edit"]
    version: Literal[1]
    roots: list[str]  # class Codes
    classes: list[BsddClass]
    properties: list[BsddProperty]
