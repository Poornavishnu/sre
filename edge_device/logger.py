"""
Logging utility for the edge device monitoring agent.
Supports JSON-formatted logs, rotating file handlers, and optional stdout printing.
"""

import json
import os
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

class Logger:
    """
    A structured logger that writes logs to a rotating file and optionally prints to stdout.
    """

   
    def __init__(
        self,
        log_path,
        device_id=None,
        print_stdout=False,
        max_bytes=1_000_000,
        backup_count=3
    ):
        """
        Initializes the logger with rotation and JSON formatting.

        Args:
            log_path (str): Path to the log file.
            device_id (str): Optional unique device identifier.
            print_stdout (bool): If True, also print logs to stdout.
            max_bytes (int): Maximum size per log file before rotation.
            backup_count (int): Number of rotated log files to keep.
        """
        self.device_id = device_id
        self.print_stdout = print_stdout

        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        self.logger = logging.getLogger(f"AgentLogger-{device_id}")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = RotatingFileHandler(
                log_path, maxBytes=max_bytes, backupCount=backup_count
            )
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, message, level="INFO"):
        """
        Logs a message with optional JSON structure and level.

        Args:
            message (str | dict): The log message or data.
            level (str): The log level, default is "INFO".
        """
        base = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": self.device_id,
            "level": level
        }

        entry = {**base, **message} if isinstance(message, dict) else {**base, "message": message}
        log_line = json.dumps(entry)
        self.logger.info(log_line)

        if self.print_stdout:
            print(f"[{level}] {entry['timestamp']}: {entry.get('message', '')}")

    def alert(self, message):
        """
        Logs a message at ALERT level.
        """
        self.log(message, level="ALERT")