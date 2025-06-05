"""
test_logger.py

Unit tests for the Logger class to verify JSON log entries are written correctly.
"""

import sys
import os
import json
import tempfile

# ✅ Add project root to sys.path first
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logger import Logger  # Must come after sys.path fix


def test_logger_writes_json_entry():
    """
    Verify that Logger.log writes a single JSON-formatted entry containing
    message, device_id, level, and timestamp.
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        log_path = tmp.name

    try:
        logger = Logger(log_path, device_id="test-device", print_stdout=False)
        logger.log("Test log entry")

        with open(log_path, "r", encoding="utf-8") as f:
            line = f.readline()
            log_data = json.loads(line)

            assert log_data["message"] == "Test log entry"
            assert log_data["device_id"] == "test-device"
            assert log_data["level"] == "INFO"
            assert "timestamp" in log_data
    finally:
        os.remove(log_path)