import os


environment = os.getenv("DJANGO_ENVIRONMENT", "dev")

if environment == "prod":
    from .production import *
else:
    from .dev import *
