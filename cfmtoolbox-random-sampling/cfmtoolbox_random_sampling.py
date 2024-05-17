from cfmtoolbox.models import CFM
from cfmtoolbox.plugins import BasePlugin


class RandomSamplingPlugin(BasePlugin):
    def process(self, model: CFM) -> CFM:
        # TODO: Process the model
        return model
