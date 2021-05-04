import requests
import argparse
import os
import pytz
import json
from datetime import datetime, timedelta
from collections import defaultdict

from tabulate import tabulate

from vaccine_scraper_utils import logging_utils, constants, meta

log = logging_utils.get_logger("vaccine3.py")

timezone = pytz.timezone(constants.TIMEZONE_IN)
today = datetime.now(timezone).strftime("%d-%m-%Y")


def get_sessions(state_name, next_seven_days=False):
    log.info("Looking for sessions today for state : '%s', date: %s", state_name, today)
    state_code = meta.get_state_code(state_name)
    if not state_code:
        log.warning("State code for state '%s' not found", state_name)
        return
    log.info("State code for '%s' = %s", state_name, state_code)
    districts_in_state = meta._list_districts_per_state(state_code=state_code)
    log.info("Districts in state '%s': %s", state_name, json.dumps(districts_in_state))
    all_sessions = meta._get_sessions(state_code, today, next_seven_days)

    district_keys = sorted(list(set([vaccination_session.get("district_name") for vaccination_session in all_sessions])))
    log.info("District keys: %s", district_keys)

    sessions_per_district = defaultdict(list)
    for dk in district_keys:
        sessions_per_district[dk] = [x for x in all_sessions if x.get("district_name") == dk]


    capacities = []

    for district, sessions in sessions_per_district.items():
        sessions_per_center_in_district = defaultdict(list)
        session_centers_in_district = sorted(
            list(
                set(
                    [x.get("name") for x in sessions]
                )
            )
        )
        for s_center in session_centers_in_district:
            centers = [x for x in sessions if x.get("name") == s_center]
            vax_sessions = []
            for ct in centers:
                vax_sessions += ct.get("sessions")
            capacities += [{"available_capacity": x.get("available_capacity"), "date": x.get("date"), "name": s_center, "district": district, "min_age_limit": x.get("min_age_limit")} for x in vax_sessions]

    available_centers = [x for x in capacities if x.get("available_capacity") >= 1]

    available_centers = [
        [
            x.get("name"),
            x.get("district"),
            x.get("available_capacity"),
            x.get("date"),
            x.get("min_age_limit")
        ] for x in available_centers
    ]

    table_headers = [
        "Center",
        "District",
        "Available",
        "Date",
        "Minimum Age Limit"
    ]

    tabulated = tabulate(available_centers, headers=table_headers)
    print(tabulated)


def main():
    parser = argparse.ArgumentParser(prog="vaccine3.py")
    parser.add_argument("-s", "--state", help="Name of the state, in lower case. For example 'andaman and nicobar'", required=True)
    parser.add_argument("-n", "--next-seven-days", help="Get sessions for the next seven days", action="store_true")

    args = parser.parse_args()

    next_seven_days = args.next_seven_days
    state = args.state

    get_sessions(state, next_seven_days)


if __name__ == "__main__":
    main()
