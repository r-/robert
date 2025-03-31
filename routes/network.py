from flask import Blueprint, jsonify
import psutil
import time

network_bp = Blueprint('network', __name__)

# Global variables to store last network reading and timestamp
last_net_io = psutil.net_io_counters()
last_time = time.time()

@network_bp.route('/network_speed')
def network_speed():
    """Returns the current network upload and download speed in Mbps."""
    global last_net_io, last_time

    current_net_io = psutil.net_io_counters()
    current_time = time.time()

    # Calculate time difference
    time_diff = current_time - last_time
    if time_diff == 0:
        time_diff = 1  # Prevent division by zero

    # Calculate differences
    bytes_sent = current_net_io.bytes_sent - last_net_io.bytes_sent
    bytes_recv = current_net_io.bytes_recv - last_net_io.bytes_recv

    sent_mbps = (bytes_sent * 8) / (time_diff * 1_000_000)  # Convert to Mbps
    recv_mbps = (bytes_recv * 8) / (time_diff * 1_000_000)  # Convert to Mbps

    # Update last readings
    last_net_io = current_net_io
    last_time = current_time

    return jsonify({
        "upload_mbps": round(sent_mbps, 2),
        "download_mbps": round(recv_mbps, 2)
    })
