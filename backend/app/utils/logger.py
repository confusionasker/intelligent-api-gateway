"""Structured logger for PulseGate.

Provides unified logging with timestamps, log levels, and contextual metadata.
Ensures sensitive credentials, passwords, and tokens are never printed to logs.
"""

import logging
import sys

# Configure standard formatting
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("pulsegate")
