from cfmtoolbox.models import CFM
from cfmtoolbox.plugins import BasePlugin


class UVLImportPlugin(BasePlugin):
    def load(self, format: str, data: bytes) -> CFM | None:
        if format != "uvl":
            return None

        cfm = CFM()  # TODO: turn data into a CFM object

        return cfm
