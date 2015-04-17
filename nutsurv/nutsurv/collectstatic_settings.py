from .settings import *  # NOQA

# setting the POSTGIS version explicetly here avoids the need
# to have a database connection for collectstatic
POSTGIS_VERSION = (2, 1, 0)
