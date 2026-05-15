from openpyxl import styles
from typing import Literal
APPDATA_OPTION = "iso_23386_settings"
SETTINGS_FILETYPE = "Settings (*.json);;all (*.*)"
ISO_FILETYPE = "XML (*.xml);;all (*.*)"
LOIN_FILETYPE = "ISO 7817-3 LOIN XML (*.xml);;all (*.*)"
MODE = Literal[ "name property set","class"]

# Format selector values used by the iso_export widget.
FORMAT_ISO_23386 = "iso_23386"
FORMAT_LOIN = "loin"
FORMAT_LABELS = {
    FORMAT_ISO_23386: "ISO 23386 XML",
    FORMAT_LOIN: "ISO 7817-3 XML (LOIN)",
}
FORMATS: tuple[str, ...] = (FORMAT_ISO_23386, FORMAT_LOIN)
