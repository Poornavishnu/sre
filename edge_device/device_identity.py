"""
Provides device identity utilities using hostname and MAC address.
"""

import socket
import uuid

def get_mac_based_device_id():
    """
    Generates a unique device ID using the MAC address.
    Format: edge-<MAC without colons>
    Example: edge-a1b2c3d4e5f6
    """
    mac = uuid.getnode()
    mac_str = f"{mac:012x}"
    return f"edge-{mac_str}"

def get_hostname():
    """
    Returns the system's hostname.
    """
    return socket.gethostname()