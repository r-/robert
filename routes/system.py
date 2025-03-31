from flask import Blueprint, render_template
import socket
import time

system_bp = Blueprint('system', __name__)

def get_server_ip():
    """Returns the server's IP address."""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

@system_bp.route('/')
def home():
    """Renders the homepage with server details."""
    start_time = time.time()
    server_ip = get_server_ip()
    latency = time.time() - start_time  # Measure request handling time

    return render_template('index.html', server_ip=server_ip, latency=latency)
