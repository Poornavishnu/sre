"""
Unit tests for monitor.py
"""

import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch
from monitor import MonitoringAgent


@patch("monitor.MetricCollector")
@patch("monitor.requests.post")
@patch("monitor.Logger")
@patch("monitor.get_mac_based_device_id", return_value="mock-device")
@patch(
    "system_check.SystemCapabilities.detect",
    return_value={"cpu": True, "memory": True, "disk": True}
)
@patch("monitor.load_config")
def test_collect_and_log(
    mock_config,
    _mock_detect,
    _mock_id,
    mock_logger,
    mock_post,
    mock_collector,
):
    """Test MonitoringAgent._collect_and_log() end-to-end with mocks."""
    # Mock the YAML config
    mock_config.return_value = {
        "metrics_to_collect": ["cpu"],
        "metrics_interval": 1,
        "cloud_endpoint": "http://mock/api",
        "device_type": "edge",
        "tags": {"zone": "a"},
    }

    # Mock the metrics collected
    mock_collector().collect.return_value = {
        "cpu_total": 90,
        "cpu_per_core": [90],
        "timestamp": "2025-06-02T00:00:00Z",
        "hostname": "mock-host",
    }

    # Mock successful POST
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status = lambda: None

    agent = MonitoringAgent()
    agent._collect_and_log()

    # Assert cloud push happened
    mock_post.assert_called_once()

    # Assert something was logged
    assert mock_logger().log.call_count >= 1