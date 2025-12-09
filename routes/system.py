"""
System initialization and routing module for R.O.B.E.R.T.

Handles IP detection, server startup announcements, and home page rendering.
"""

from flask import Blueprint, render_template
import time
import logging
from typing import Optional
from routes.network import set_local_ip
from routes.speech import speak_text
import netifaces as ni

# Blueprint configuration
system_bp = Blueprint('system', __name__)

# Logger setup
logger = logging.getLogger(__name__)


def detect_local_ip() -> Optional[str]:
    """
    Detect the local IP address of the robot.
    
    Attempts to get the IP from WiFi interface first (wlan0),
    then falls back to Ethernet (eth0).
    
    Returns:
        Optional[str]: Local IP address or None if detection fails
    """
    interfaces_to_try = ['wlan0', 'eth0', 'en0']  # WiFi, Ethernet, macOS WiFi
    
    for interface in interfaces_to_try:
        try:
            addresses = ni.ifaddresses(interface)
            if ni.AF_INET in addresses:
                ip = addresses[ni.AF_INET][0]['addr']
                logger.info(f"Detected IP from {interface}: {ip}")
                return ip
        except (ValueError, KeyError) as e:
            logger.debug(f"Interface {interface} not available: {e}")
            continue
    
    logger.error("Failed to detect local IP from any network interface")
    return None


@system_bp.route('/')
def home() -> str:
    """
    Render the home page with server configuration details.
    
    This is the main entry point for the web dashboard.
    Measures request latency and announces the server through speech.
    
    Returns:
        str: Rendered HTML template
    """
    start_time = time.time()
    
    # Detect and set local IP
    server_ip = detect_local_ip()
    
    if server_ip is None:
        logger.error("Could not detect server IP, using localhost")
        server_ip = "127.0.0.1"
    
    # Register the IP with the network module
    set_local_ip(server_ip)
    
    # Calculate request latency
    latency = time.time() - start_time
    
    logger.info(f"Server home page accessed. Local IP: {server_ip}, Latency: {latency:.2f}ms")
    
    # Announce server startup via speech
    try:
        speak_text(f"Server running on {server_ip}")
    except Exception as e:
        logger.warning(f"Failed to announce server via speech: {e}")
    
    # Render template with server information
    return render_template(
        'index.html',
        server_ip=server_ip,
        latency=f"{latency * 1000:.2f}ms"
    )
