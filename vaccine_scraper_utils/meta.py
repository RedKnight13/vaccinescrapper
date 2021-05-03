"""
Code to fetch meta-data from the API
"""

import requests

from cachetools import cached
import redis

from . import logging_utils, constants

log = logging_utils.get_logger("meta.py")


@cached({})
def __redis_connection():
    log.info("Spinning up redis")
    return redis.Redis(host="127.0.0.1", port=6379)


@cached({})
def _fetch_states():
    end_point = "admin/location/states"
    api_url = "{base}/{resource}".format(
        base=constants.API_BASE,
        resource=end_point
    )
    cache_connection = __redis_connection()
    states = {}
    try:
        _from_cache = cache_connection.hgetall(constants.REDIS_HMKEY_STATES)
        if _from_cache:
            log.info("Fetched state info from Redis. Not calling API")
            return _from_cache

        log.info("Will hit this API endpoint: %s", api_url)
        res = requests.get(url=api_url)
        res.raise_for_status()
        states = res.json()
        states = states.get("states")

        # save state information to redis
        for st in states:
            cache_connection.hset(constants.REDIS_HMKEY_STATES, st.get("state_name").lower(), st.get("state_id"))

        return states
    except requests.HTTPError as ht_err:
        log.exception("An error occured while hitting %s. Details: %s", api_url, ht_err)


@cached({})
def _list_districts_per_state(state_code: str):
    end_point = "admin/location/districts/{state_code}".format(state_code=state_code)
    api_url = "{base}/{resource}".format(
        base=constants.API_BASE,
        resource=end_point
    )
    log.info("Fetching data for state code %s. API URL: %s", state_code, api_url)
    districts_in_state = {}
    try:
        state_districts_key = constants.REDIS_HMKEY_DISTRICTS.format(state_id=state_code)
        cache_connection = __redis_connection()
        districts_in_state = cache_connection.hgetall(state_districts_key)
        if districts_in_state:
            districts_in_state = {
                k.decode("utf-8"): v.decode("utf-8") for k, v in districts_in_state.items()
            }

        res = requests.get(api_url)
        res.raise_for_status()
        districts_in_state = res.json().get("districts")
        districts_in_state = {
            x.get("district_name").lower(): x.get("district_id") for x in districts_in_state
        }
        for k, v in districts_in_state.items():
            cache_connection.hset(state_districts_key, k, v)
        return districts_in_state
    except requests.HTTPError as ht_err:
        log.exception("An error occured while hitting %s. Details: %s", api_url, ht_err)


def get_state_code(state_name: str):
    states = _fetch_states()
    log.info("Looking up state code for '%s'", state_name)
    for k, v in states.items():
        if k.decode("utf-8") == state_name:
            return v.decode("utf-8")


def _get_sessions(state_code, dt, next_seven_days=False):
    api_url_template = "{base}/{endpoint}"
    endpoints = []
    districts = _list_districts_per_state(state_code=state_code)
    end_point_template = "appointment/sessions/public/replace-me?district_id={did}&date={dt}"
    endpoints = [
        end_point_template.format(
            did=v,
            dt=dt
        ) for v in districts.values()
    ]
    if not next_seven_days:
        endpoints = [x.replace("replace-me", "findByDistrict") for x in endpoints]
    else:
        endpoints = [x.replace("replace-me", "calendarByDistrict") for x in endpoints]

    common_headers = {
        "accept": "application/json",
        "Accept-Language": "en_US"
    }

    sessions = []

    for ep in endpoints:
        api_url = api_url_template.format(base=constants.API_BASE, endpoint=ep)
        log.info("API URL generated: %s", api_url)
        try:
            res = requests.get(api_url, headers=common_headers)
            res.raise_for_status()
            content = res.json()
            centers = content.get("centers")
            sessions += centers
        except requests.HTTPError as ht_err:
            log.exception("An error occured while hitting URL '%s'. Details: %s", api_url, ht_err)

    return sessions
