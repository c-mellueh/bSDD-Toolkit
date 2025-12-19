from __future__ import annotations
from . import constants,ui


class GraphViewerNodeProperties:
    def __init__(self):
        self.filters: dict[str, bool] = {nt: True for nt in constants.ALLOWED_NODE_TYPES}
        self.nodes:list[ui.Node] = list()