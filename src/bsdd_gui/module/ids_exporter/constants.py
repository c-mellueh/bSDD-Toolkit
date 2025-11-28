SETTINGS_FILETYPE = "Settings (*.json);;all (*.*)"
IDS_FILETYPE = "IDS (*.ids);;XML(*.xml);;all (*.*)"
IDS_APPDATA = "ids_settings"

DATATYPE_MAPPING = {
    "String": "IfcLabel",
    "Boolean": "IfcBoolean",
    "Integer": "IfcInteger",
    "Real": "IfcReal",
    "Character": "IfcLabel",
    "Time": "IfcDateTime",
}

PROPERTY_DATATYPE_MAPPING = {
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/AcousticRating": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/CapacityPeople": "IfcCountMeasure",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/ClearDepth": "IfcPositiveLengthMeasure",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/ClearHeight": "IfcPositiveLengthMeasure",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/ClearWidth": "IfcPositiveLengthMeasure",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/ExposureClass": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/FireRating": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/Height": "IfcPositiveLengthMeasure",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/ModelReference": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/SecurityRating": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/StrengthClass": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/StructuralClass": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/SurfaceSpreadOfFlame": "IfcLabel",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/ThermalTransmittance": "IfcThermalTransmittanceMeasure",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/TileLength": "IfcPositiveLengthMeasure",
    "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/TileWidth": "IfcPositiveLengthMeasure",
}