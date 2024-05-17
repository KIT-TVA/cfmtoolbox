from cfmtoolbox.models import CFM
from cfmtoolbox.plugins import BasePlugin


class UVLExportPlugin(BasePlugin):
    def save(self, format: str, cfm: CFM) -> bytes | None:
        if format != "uvl":
            return None

        data = b""  # TODO: turn cfm into bytes

        return data
