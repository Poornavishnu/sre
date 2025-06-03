"""
test_metrics.py

Unit tests for MetricCollector to verify that CPU, memory, and disk metrics
are collected as expected when the corresponding capability is present.
"""

import sys
import os

# Ensure import from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from metrics import MetricCollector
from system_check import SystemCapabilities 

capabilities = SystemCapabilities().detect()


def test_collect_cpu_metrics():
    """
    Verify that MetricCollector.collect() returns 'cpu_total' and 'cpu_per_core'
    when 'cpu' is requested and supported.
    """
    collector = MetricCollector(["cpu"], capabilities)
    metrics = collector.collect()
    assert "cpu_total" in metrics
    assert "cpu_per_core" in metrics
    assert isinstance(metrics["cpu_per_core"], list)


def test_collect_memory_metrics():
    """
    Verify that MetricCollector.collect() returns 'memory_total', 'memory_used',
    and 'memory_percent' when 'memory' is requested and supported.
    """
    collector = MetricCollector(["memory"], capabilities)
    metrics = collector.collect()
    assert "memory_total" in metrics
    assert "memory_used" in metrics
    assert "memory_percent" in metrics


def test_collect_disk_metrics():
    """
    Verify that MetricCollector.collect() returns 'disk_total', 'disk_used',
    and 'disk_percent' when 'disk' is requested and supported.
    """
    collector = MetricCollector(["disk"], capabilities)
    metrics = collector.collect()
    assert "disk_total" in metrics
    assert "disk_used" in metrics
    assert "disk_percent" in metrics