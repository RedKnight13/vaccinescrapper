import pytest
from vaccine_scraper_utils import logging_utils

def test_logging():
    log = logging_utils.get_logger("test_logging")
    log.info("Hello world!")
    assert log != None

