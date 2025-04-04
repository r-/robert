from flask import Blueprint, jsonify, request
import psutil
import time
import requests
import socket

network_bp = Blueprint('network', __name__)

health = 10

connected_players = {}
connected_server_address = None  # Store the server URL globally

local_ip = None

# Global variables to store last network reading and timestamp
last_net_io = psutil.net_io_counters()
last_time = time.time()

def set_local_ip(newIP):
    global local_ip
    local_ip = newIP

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

def get_address():
    global connected_server_address
    return connected_server_address

@network_bp.route('/get_health')
def get_health():
    global health
    max_health = 10  # Example max health
    
    # Debugging output
    print(f"Returning health data: currentHealth = {health}, maxHealth = {max_health}")
    
    return jsonify({
        'currentHealth': health,
        'maxHealth': max_health
    })

@network_bp.route('/set_health', methods=['POST'])
def set_health():
    global health
    
    # Get JSON data from the request body
    data = request.get_json()
    
    # Check if 'status' key exists in the data
    if 'status' in data:
        new_health = data['status']
        
        # Check that the new health value is a valid number and within bounds (optional)
        if isinstance(new_health, int) and new_health >= 0:
            health = new_health
            return jsonify({'message': 'Health status updated successfully!'}), 200
        else:
            return jsonify({'error': 'Invalid health value. Must be a non-negative integer.'}), 400
    else:
        return jsonify({'error': 'Bad request, missing "status" key.'}), 400

import requests

@network_bp.route('/command', methods=['POST'])
def handle_command():
    global connected_server_address
    data = request.get_json()

    command = data.get('command')
    if command and command.startswith('/login'):
        # Extract the server IP and player ID from the command
        parts = command.split()
        if len(parts) < 3:
            return jsonify({"status": "error", "message": "Usage: /login <server_ip> <player_id>"}), 400

        new_server_ip = parts[1]
        player_id = parts[2]
        print(local_ip)
        print(player_id)

        # Update the server_url
        connected_server_address = f"http://{new_server_ip}"

        # Send the /login command to the server
        try:
            login_data = {"command": f"/login {local_ip} {player_id}"}
            response = requests.post(f"{connected_server_address}/command", json=login_data)
            if response.status_code == 200:
                return jsonify({"status": "success", "message": f"Logged in successfully as Player {player_id} to {connected_server_address}."})
            else:
                return jsonify({"status": "error", "message": "Failed to connect to the server."}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "message": f"Error connecting to server: {str(e)}"}), 500

    return jsonify({"status": "error", "message": "Invalid command."}), 400