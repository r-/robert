from flask import Blueprint, render_template
import socket
import time
from routes.network import set_local_ip
import netifaces as ni

system_bp = Blueprint('system', __name__)

def get_local_ip():
    # Get the default network interface (usually 'eth0' or 'wlan0' for Wi-Fi)
    try:
        # This retrieves the IP address of the default network interface (Wi-Fi or Ethernet)
        ni.ifaddresses('wlan0')  # 'wlan0' for Wi-Fi interface
        ip_address = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    except ValueError:
        # In case 'wlan0' isn't available, fallback to other interfaces like 'eth0'
        ni.ifaddresses('eth0')  # Ethernet interface fallback
        ip_address = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    return ip_address

@system_bp.route('/')
def home():
    """Renders the homepage with server details."""
    start_time = time.time()
    server_ip = get_local_ip()
    latency = time.time() - start_time  # Measure request handling time
    set_local_ip(server_ip)
    print(f"Local ip {server_ip}")
    return render_template('index.html', server_ip=server_ip, latency=latency)
