"""
The last running settings page will overwrite the other pages and take control.
Comment out necessary pages to run off the appropriate settings.
"""
from decouple import config

# from .base import *

# from .production import *


if config('VERSION') == 'PROD':
    from .production import *
else:
    from .local import *
