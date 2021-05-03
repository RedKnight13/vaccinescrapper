import pytest

from vaccine_scraper_utils.meta import _fetch_states, _list_districts_per_state, get_state_code

def test__fetch_states():
    states = _fetch_states()

    assert type(states) == dict
    assert len(states.keys()) >= 1


def test__list_districts_per_state():
    states = _fetch_states()
    for st_code in states.values():
        districts_in_state = _list_districts_per_state(st_code.decode("utf-8"))
        assert type(districts_in_state) == dict
        assert len(districts_in_state.keys()) >= 1


def test_get_state_code():
    states = _fetch_states()
    for st_name in states.keys():
        code = get_state_code(st_name.decode("utf-8"))
        assert code != None
