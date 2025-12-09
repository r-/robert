"""
Network management and communication module for R.O.B.E.R.T.

Handles network monitoring, server communication, and game state management.
"""

from flask import Blueprint, jsonify, request
import psutil
import time
import requests
import logging
from typing import Optional, Dict, Tuple

# Blueprint configuration
network_bp = Blueprint('network', __name__)

# Logger setup
logger = logging.getLogger(__name__)

# ==================== Global State ====================
# Game/Network state
current_health = 4
MAX_HEALTH = 4

# Server connection state
connected_players: Dict[str, str] = {}
connected_server_address: Optional[str] = None
local_ip_address: Optional[str] = None
player_id: Optional[str] = None
player_code: Optional[int] = None

# Network statistics tracking
last_net_io = psutil.net_io_counters()
last_time = time.time()


# ==================== Setter Functions ====================
def set_local_ip(ip: str) -> None:
    """
    Set the local IP address of the robot.
    
    Args:
        ip (str): Local IP address
    """
    global local_ip_address
    local_ip_address = ip
    logger.info(f"Local IP configured: {local_ip_address}")


# ==================== Getter Functions ====================
def get_local_ip() -> Optional[str]:
    """
    Get the configured local IP address.
    
    Returns:
        Optional[str]: Local IP address or None if not configured
    """
    return local_ip_address


def get_server_address() -> Optional[str]:
    """
    Get the connected server address.
    
    Returns:
        Optional[str]: Server address or None if not connected
    """
    return connected_server_address


def get_player_id() -> Optional[str]:
    """
    Get the current player ID.
    
    Returns:
        Optional[str]: Player ID or None if not joined
    """
    return player_id


def set_player_info(p_id: str, p_code: int) -> None:
    """
    Set player information after joining a game.
    
    Args:
        p_id (str): Player ID from server
        p_code (int): Player code used to join
    """
    global player_id, player_code
    player_id = p_id
    player_code = p_code
    logger.info(f"Player registered: ID={p_id}, Code={p_code}")


# ==================== Network Monitoring Routes ====================
@network_bp.route('/network_speed')
def network_speed() -> Tuple[dict, int]:
    """
    Get current network upload and download speeds.
    
    Returns:
        tuple: (JSON response with speeds in Mbps, HTTP status code)
    """
    global last_net_io, last_time
    
    try:
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        
        # Calculate time difference, prevent division by zero
        time_diff = max(current_time - last_time, 0.001)
        
        # Calculate byte differences
        bytes_sent = current_net_io.bytes_sent - last_net_io.bytes_sent
        bytes_recv = current_net_io.bytes_recv - last_net_io.bytes_recv
        
        # Convert to Mbps
        sent_mbps = (bytes_sent * 8) / (time_diff * 1_000_000)
        recv_mbps = (bytes_recv * 8) / (time_diff * 1_000_000)
        
        # Update tracking variables
        last_net_io = current_net_io
        last_time = current_time
        
        logger.debug(f"Network speed - Up: {sent_mbps:.2f} Mbps, Down: {recv_mbps:.2f} Mbps")
        
        return jsonify({
            "upload_mbps": round(sent_mbps, 2),
            "download_mbps": round(recv_mbps, 2)
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating network speed: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to calculate network speed"
        }), 500


# ==================== Health Management Routes ====================
@network_bp.route('/get_health', methods=['GET'])
def get_health() -> Tuple[dict, int]:
    """
    Get the robot's current health status.
    
    Returns:
        tuple: (JSON response with health values, HTTP status code)
    """
    logger.debug(f"Health status requested: {current_health}/{MAX_HEALTH}")
    return jsonify({
        'current_health': current_health,
        'max_health': MAX_HEALTH
    }), 200


@network_bp.route('/set_health', methods=['POST'])
def set_health() -> Tuple[dict, int]:
    """
    Set the robot's health status.
    
    Expected JSON payload:
        {
            "status": <int>  # Health value (must be non-negative)
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    global current_health
    
    data = request.get_json()
    
    if not data or 'status' not in data:
        logger.warning("Set health request missing 'status' field")
        return jsonify({
            'error': 'Missing required field: "status"'
        }), 400
    
    try:
        new_health = int(data['status'])
        
        if new_health < 0:
            logger.warning(f"Attempt to set invalid health value: {new_health}")
            return jsonify({
                'error': 'Health value must be non-negative'
            }), 400
        
        current_health = new_health
        logger.info(f"Health updated to: {current_health}")
        
        return jsonify({
            'message': 'Health status updated successfully',
            'current_health': current_health
        }), 200
        
    except ValueError:
        logger.error("Invalid health value type in request")
        return jsonify({
            'error': 'Health value must be an integer'
        }), 400


# ==================== Server Communication Routes ====================
@network_bp.route('/command', methods=['POST'])
def handle_command() -> Tuple[dict, int]:
    """
    Handle commands from the server, including login.
    
    Supports:
        /login <server_ip> <player_id> - Connect to a game server
    
    Expected JSON payload:
        {
            "command": "<command_string>"
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    global connected_server_address
    
    data = request.get_json()
    
    if not data or 'command' not in data:
        logger.warning("Command request missing 'command' field")
        return jsonify({
            "status": "error",
            "message": "Missing required field: 'command'"
        }), 400
    
    command = data.get('command', '').strip()
    
    # Handle login command
    if command.startswith('/login'):
        return handle_login_command(command)
    
    logger.warning(f"Unknown command: {command}")
    return jsonify({
        "status": "error",
        "message": "Unknown command"
    }), 400


def handle_login_command(command: str) -> Tuple[dict, int]:
    """
    Handle the /login command to connect to a game server.
    
    Args:
        command (str): Login command string
        
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    global connected_server_address
    
    parts = command.split()
    if len(parts) < 3:
        logger.warning(f"Invalid login command format: {command}")
        return jsonify({
            "status": "error",
            "message": "Usage: /login <server_ip> <player_id>"
        }), 400
    
    server_ip = parts[1]
    player_id = parts[2]
    
    # Update server address
    connected_server_address = f"http://{server_ip}"
    logger.info(f"Attempting to login as player {player_id} to {connected_server_address}")
    
    # Send login request to server
    try:
        login_payload = {
            "command": f"/login {local_ip_address} {player_id}"
        }
        
        response = requests.post(
            f"{connected_server_address}/command",
            json=login_payload,
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully logged in as player {player_id}")
            return jsonify({
                "status": "success",
                "message": f"Logged in successfully as Player {player_id}"
            }), 200
        else:
            logger.error(f"Server rejected login: {response.status_code}")
            return jsonify({
                "status": "error",
                "message": "Server rejected login attempt"
            }), 500
            
    except requests.exceptions.Timeout:
        logger.error(f"Login request timed out to {connected_server_address}")
        return jsonify({
            "status": "error",
            "message": "Connection to server timed out"
        }), 500
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to server: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to connect to server: {str(e)}"
        }), 500
