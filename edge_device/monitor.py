"""
monitor.py

Module for running the edge device MonitoringAgent, which collects metrics
and pushes them to a cloud endpoint.
"""

import time
import os
from datetime import datetime, timezone

import requests

from config_loader import load_config
from metrics import MetricCollector
from logger import Logger
from system_check import SystemCapabilities
from device_identity import get_mac_based_device_id


class MonitoringAgent:
    """
    MonitoringAgent initializes configuration, filters unsupported metrics,
    logs startup information, and then enters a loop to collect+log+push metrics.
    """

    def __init__(self, config_path="config.yaml"):
        """
        :param config_path: Path to YAML config file (defaults to "config.yaml")
        """
        config = load_config(config_path)

        # ─── Group 1: identity-related fields ──────────────────────────────────────
        self.identity = {
            "device_id": get_mac_based_device_id(),
            "device_type": config.get("device_type", "unknown"),
            "tags": config.get("tags", {}),
        }

        # ─── Group 2: settings-related fields ──────────────────────────────────────
        self.settings = {
            "interval": config.get("metrics_interval", 10),
            "cloud_endpoint": config.get("cloud_endpoint"),
            "metrics_to_collect": config.get("metrics_to_collect", []),
        }

        # Detect system capabilities once at startup
        self.capabilities = SystemCapabilities().detect()

        # ─── Logger setup ──────────────────────────────────────────────────────────
        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", f"{self.identity['device_id']}.log")
        self.logger = Logger(log_path, device_id=self.identity["device_id"], print_stdout=True)

        # Filter out any unsupported metrics and update settings in place
        self.settings["metrics_to_collect"] = self._filter_supported_metrics()
        self._log_startup()

    def _filter_supported_metrics(self):
        """
        Remove any requested metrics that the current device does not support.
        Logs a warning for each skipped metric.
        :return: Filtered list of metrics that are supported
        """
        requested = self.settings["metrics_to_collect"]
        unsupported = [m for m in requested if not self.capabilities.get(m)]
        if unsupported:
            self.logger.log(f" Skipping unsupported metrics: {unsupported}", level="WARN")
        return [m for m in requested if self.capabilities.get(m)]

    def _log_startup(self):
        """
        Log a startup entry containing timestamp, device_id, device_type,
        requested metrics, detected capabilities, and any user tags.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": self.identity["device_id"],
            "device_type": self.identity["device_type"],
            "metrics_requested": self.settings["metrics_to_collect"],
            "capabilities": self.capabilities,
            "tags": self.identity["tags"],
        }
        self.logger.log(entry)

    def _collect_and_log(self):
        """
        Collect metrics via MetricCollector, attach a heartbeat,
        write the combined log entry, and then push raw metrics to cloud.
        """
        collector = MetricCollector(self.settings["metrics_to_collect"], self.capabilities)
        metrics = collector.collect()
        metrics["heartbeat"] = 1

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": self.identity["device_id"],
            "device_type": self.identity["device_type"],
            "metrics": metrics,
            "tags": self.identity["tags"],
        }

        self.logger.log(log_entry)
        print(f"[{self.identity['device_id']}] Metrics collected at {log_entry['timestamp']}")
        self._send_to_cloud(metrics)

    def _send_to_cloud(self, metrics, max_retries=3, retry_delay=2):
        """
        Flatten metrics into a single JSON payload (including device_id/device_type/tags),
        then POST to self.settings['cloud_endpoint'] with up to max_retries.
        Any requests-related failure is caught and logged.

        :param metrics: Dictionary of collected metrics
        :param max_retries: Number of retry attempts if a push fails
        :param retry_delay: Base delay (in seconds) between retries (multiplied by attempt number)
        """
        endpoint = self.settings["cloud_endpoint"]
        if not endpoint:
            return

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": self.identity["device_id"],
            "device_type": self.identity["device_type"],
            "tags": self.identity["tags"],
            **metrics,
        }

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(endpoint, json=payload, timeout=5)
                response.raise_for_status()
                return
            except requests.RequestException as err:
                self.logger.log(f"Cloud push attempt {attempt} failed: {err}", level="ERROR")
                if attempt < max_retries:
                    time.sleep(retry_delay * attempt)
                else:
                    self.logger.log("All cloud push attempts failed", level="ERROR")

    def run(self):
        """
        Enter an infinite loop: collect + log + send metrics, then sleep for self.settings["interval"] seconds.
        """
        while True:
            self._collect_and_log()
            time.sleep(self.settings["interval"])


if __name__ == "__main__":
    agent = MonitoringAgent()
    agent.run()