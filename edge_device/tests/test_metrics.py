"""
test_metrics.py

Unit tests for MetricCollector and EdgeAgent using mocked capabilities.
"""

import sys
import os

# Ensure import from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from metrics import MetricCollector, EdgeAgent

# ✅ Mocked capabilities
mock_capabilities = {
    "cpu": True,
    "memory": True,
    "disk": True,
    "battery": False
}


def test_collect_cpu_metrics():
    collector = MetricCollector(["cpu"], mock_capabilities)
    metrics = collector.collect()
    assert metrics is not None
    assert "cpu_total" in metrics
    assert "cpu_per_core" in metrics
    assert isinstance(metrics["cpu_per_core"], list)


def test_collect_memory_metrics():
    collector = MetricCollector(["memory"], mock_capabilities)
    metrics = collector.collect()
    assert metrics is not None
    assert "memory_total" in metrics
    assert "memory_used" in metrics
    assert "memory_percent" in metrics


def test_collect_disk_metrics():
    collector = MetricCollector(["disk"], mock_capabilities)
    metrics = collector.collect()
    assert metrics is not None
    assert "disk_total" in metrics
    assert "disk_used" in metrics
    assert "disk_percent" in metrics


def test_edge_agent_collects_all_metrics():
    config = {
        "metrics_to_collect": ["cpu", "memory", "disk"]
    }
    agent = EdgeAgent(config)
    metrics = agent.run()
    assert metrics is not None
    assert "cpu_total" in metrics
    assert "memory_total" in metrics
    assert "disk_total" in metrics