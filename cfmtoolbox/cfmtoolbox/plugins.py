from cfmtoolbox.models import CFM


class BasePlugin:
    def load(self, format: str, data: bytes) -> CFM | None:
        """
        Only implement this method if the plugin supports loading a model from a file.
        Return None if the plugin does not support the given format.
        """
        raise NotImplementedError

    def dump(self, format: str, model: CFM) -> bytes | None:
        """
        Only implement this method if the plugin supports dumping a model to a file.
        Return None if the plugin does not support the given format.
        """
        raise NotImplementedError

    def process(self, model: CFM) -> CFM:
        """
        Only implement this method if the plugin supports processing of a model.
        """
        raise NotImplementedError
