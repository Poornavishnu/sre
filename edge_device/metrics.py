"""
metrics.py

Module for detecting system capabilities and collecting system metrics
for edge device monitoring.
"""

import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List

import psutil


class SystemCapabilities:
    """
    Detect available system capabilities, such as CPU, memory, disk, temperature,
    battery, and GPU support.
    """

    def __init__(self):
        self.capabilities = {
            "cpu": True,
            "memory": True,
            "disk": True,
            "temperature": False,
            "battery": False,
            "gpu": False,
        }

    def detect(self) -> Dict[str, bool]:
        """
        Run all checks and return a dictionary indicating which metrics are supported.
        """
        self._check_cpu()
        self._check_memory()
        self._check_disk()
        self._check_temperature()
        self._check_battery()
        self._check_gpu()
        return self.capabilities

    def _check_cpu(self):
        """
        Verify that CPU utilization metrics can be retrieved.
        """
        try:
            psutil.cpu_percent()
        except psutil.Error:
            self.capabilities["cpu"] = False

    def _check_memory(self):
        """
        Verify that memory utilization metrics can be retrieved.
        """
        try:
            psutil.virtual_memory()
        except psutil.Error:
            self.capabilities["memory"] = False

    def _check_disk(self):
        """
        Verify that disk usage metrics can be retrieved.
        """
        try:
            psutil.disk_usage("/")
        except psutil.Error:
            self.capabilities["disk"] = False

    def _check_temperature(self):
        """
        Check if temperature sensors are available.
        """
        try:
            temps = psutil.sensors_temperatures()
            if temps and any(temps.values()):
                self.capabilities["temperature"] = True
        except (AttributeError, NotImplementedError, psutil.Error):
            self.capabilities["temperature"] = False

    def _check_battery(self):
        """
        Check if battery information is available.
        """
        try:
            batt = psutil.sensors_battery()
            if batt is not None:
                self.capabilities["battery"] = True
        except (AttributeError, NotImplementedError, psutil.Error):
            self.capabilities["battery"] = False

    def _check_gpu(self):
        """
        Check if NVIDIA GPU is available by running 'nvidia-smi'.
        """
        try:
            gpu_proc = subprocess.run(
                ["nvidia-smi"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if gpu_proc.returncode == 0:
                self.capabilities["gpu"] = True
        except FileNotFoundError:
            self.capabilities["gpu"] = False


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

        if "temperature" in self.metrics_to_collect and self.capabilities.get("temperature", False):
            try:
                temps = psutil.sensors_temperatures()
                metrics["temperature"] = {
                    name: [sensor.current for sensor in readings]
                    for name, readings in temps.items()
                }
            except (AttributeError, NotImplementedError, psutil.Error):
                pass

        if "battery" in self.metrics_to_collect and self.capabilities.get("battery", False):
            try:
                batt = psutil.sensors_battery()
                if batt:
                    metrics["battery_percent"] = batt.percent
                    metrics["power_plugged"] = batt.power_plugged
            except (AttributeError, NotImplementedError, psutil.Error):
                pass

        if "gpu" in self.metrics_to_collect and self.capabilities.get("gpu", False):
            metrics["gpu_status"] = "NVIDIA GPU detected"

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
        "metrics_to_collect": ["cpu", "memory", "disk", "temperature", "battery", "gpu"],
    }

    agent = EdgeAgent(sample_config)
    collected = agent.run()
    print("Collected Metrics:", collected)