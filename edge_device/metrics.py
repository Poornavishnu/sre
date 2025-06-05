"""
metrics.py

Module for detecting system capabilities and collecting system metrics
for edge device monitoring.
"""

import platform
import shutil
import sys
from datetime import datetime, timezone
from typing import Dict, List
from system_check import SystemCapabilities 
import psutil


class MetricCollector:
    """
    Collect specified system metrics based on detected capabilities.
    """

    def __init__(self, metrics_to_collect: List[str], capabilities: Dict[str, bool]):
        """
        :param metrics_to_collect: List of metric names to collect (e.g., ["cpu", "memory", "disk"])
        :param capabilities: Dictionary of detected capabilities from SystemCapabilities.detect()
        """
        self.metrics_to_collect = metrics_to_collect
        self.capabilities = capabilities

    def collect(self) -> Dict:
        """
        Gather the requested metrics and return them in a dictionary.
        """
        metrics: Dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hostname": platform.node(),
        }

        if "cpu" in self.metrics_to_collect and self.capabilities.get("cpu", False):
            # Seed baseline for accurate readings
            psutil.cpu_percent(interval=None)
            metrics["cpu_total"] = psutil.cpu_percent(interval=0.5)
            metrics["cpu_per_core"] = psutil.cpu_percent(interval=0.5, percpu=True)

        if "memory" in self.metrics_to_collect and self.capabilities.get("memory", False):
            mem = psutil.virtual_memory()
            metrics["memory_percent"] = mem.percent
            metrics["memory_used"] = mem.used
            metrics["memory_total"] = mem.total

        if "disk" in self.metrics_to_collect and self.capabilities.get("disk", False):
            disk = psutil.disk_usage("/")
            metrics["disk_percent"] = disk.percent
            metrics["disk_used"] = disk.used
            metrics["disk_total"] = disk.total

        if "battery" in self.metrics_to_collect and self.capabilities.get("battery", False):
            try:
                batt = psutil.sensors_battery()
                if batt:
                    metrics["battery_percent"] = batt.percent
                    metrics["power_plugged"] = batt.power_plugged
            except (AttributeError, NotImplementedError, psutil.Error):
                pass
        return metrics


class EdgeAgent:
    """
    EdgeAgent ties together capability detection and metric collection.
    """

    def __init__(self, config: Dict):
        """
        :param config: Configuration dictionary that must include "metrics_to_collect" key
        """
        capabilities = SystemCapabilities().detect()
        self.collector = MetricCollector(config.get("metrics_to_collect", []), capabilities)

    def run(self) -> Dict:
        """
        Execute a single collection cycle and return the collected metrics.
        """
        return self.collector.collect()


if __name__ == "__main__":
    # Ensure Python 3 is available
    if not shutil.which("python3"):
        print("Python 3 not found!")
        sys.exit(1)

    sample_config = {
        "metrics_to_collect": ["cpu", "memory", "disk", "battery"],
    }

    agent = EdgeAgent(sample_config)
    collected = agent.run()
    print("Collected Metrics:", collected)