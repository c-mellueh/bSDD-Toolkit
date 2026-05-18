from bsdd_gui.presets.ui_presets import TagInput


class TagInput_IfcVersion(TagInput):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, allowed=["IFC2X3", "IFC4", "IFC4X3_ADD2"], minimum_le_width=100, **kwargs
        )
