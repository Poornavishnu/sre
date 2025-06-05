# test_system_check.py

import sys
import os
import pytest

# Make project root visible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from system_check import SystemCapabilities

def test_detect_returns_dict():
    detector = SystemCapabilities()
    capabilities = detector.detect()
    assert isinstance(capabilities, dict)

def test_cpu_check_flag_type():
    detector = SystemCapabilities()
    capabilities = detector.detect()
    assert isinstance(capabilities["cpu"], bool)

def test_memory_check_flag_type():
    detector = SystemCapabilities()
    capabilities = detector.detect()
    assert isinstance(capabilities["memory"], bool)

def test_disk_check_flag_type():
    detector = SystemCapabilities()
    capabilities = detector.detect()
    assert isinstance(capabilities["disk"], bool)

def test_battery_flag_type():
    detector = SystemCapabilities()
    capabilities = detector.detect()
    assert isinstance(capabilities["battery"], bool)