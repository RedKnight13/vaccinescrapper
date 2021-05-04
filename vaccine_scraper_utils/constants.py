"""
Describes all the constants needed to access the API
"""

import os

API_HOSTNAME = "https://cdn-api.co-vin.in"
API_BASE_PATH = "api"
API_VERSION = "v2"

API_BASE = "{host}/{base_path}/{version}".format(
    host=API_HOSTNAME,
    base_path=API_BASE_PATH,
    version=API_VERSION
)


REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_HMKEY_STATES = "states"
REDIS_HMKEY_DISTRICTS = "state_{state_id}"

TIMEZONE_IN = "Asia/Kolkata"
