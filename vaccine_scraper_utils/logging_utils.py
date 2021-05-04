"""
Spins up a logger
"""

import logging

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] - %(name)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s")

def get_logger(logger_name: str):
    return logging.getLogger(name=logger_name)
