from .models import CFM
from .toolbox import CFMToolbox

app = CFMToolbox()

__all__ = [
    "app",
    "CFM",
]
