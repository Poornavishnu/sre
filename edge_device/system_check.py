"""
system_check.py

Detect available system capabilities, such as CPU, memory, disk, temperature,
battery.
"""

import psutil
from typing import Dict


class SystemCapabilities:
    """
    Detects system capabilities by attempting to access various hardware metrics
    using psutil and system tools.
    """

    def __init__(self):
        self.capabilities: Dict[str, bool] = {
            "cpu": True,
            "memory": True,
            "disk": True,
            "battery": False,
        }

    def detect(self) -> Dict[str, bool]:
        """
        Runs all checks and returns a dictionary of capability flags.
        """
        self._check_cpu()
        self._check_memory()
        self._check_disk()
        self._check_battery()
        return self.capabilities

    def _check_cpu(self):
        """Check if CPU metrics can be accessed."""
        try:
            psutil.cpu_percent()
        except psutil.Error:
            self.capabilities["cpu"] = False

    def _check_memory(self):
        """Check if memory metrics can be accessed."""
        try:
            psutil.virtual_memory()
        except psutil.Error:
            self.capabilities["memory"] = False

    def _check_disk(self):
        """Check if disk usage metrics can be accessed."""
        try:
            psutil.disk_usage("/")
        except psutil.Error:
            self.capabilities["disk"] = False

    def _check_battery(self):
        """Check if battery metrics are available."""
        try:
            batt = psutil.sensors_battery()
            if batt is not None:
                self.capabilities["battery"] = True
        except (AttributeError, NotImplementedError, psutil.Error):
            self.capabilities["battery"] = False