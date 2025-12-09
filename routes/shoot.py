"""
Shooting and target management module for R.O.B.E.R.T.

Handles target detection, validation, and communication with game server.
"""

from flask import Blueprint, jsonify
from routes.network import get_server_address, get_local_ip
import time
import logging
from threading import Lock
from typing import Optional, List
import requests
from tools.RetainedList import RetainedList
from config import Config

# Blueprint configuration
shoot_bp = Blueprint('shoot', __name__)

# Logger setup
logger = logging.getLogger(__name__)

# ==================== Global State ====================
# Cooldown configuration
SHOOT_COOLDOWN_TIME = 2  # Seconds between shots
last_shot_time = 0

# Target tracking
qr_codes = RetainedList(
    retention_frames=Config.CAMERA_FRAMERATE,
    frame_delay=(1 / Config.CAMERA_FRAMERATE)
)
qr_codes.start()


def update_targets(new_targets: List[str]) -> None:
    """
    Update the list of currently detected targets.
    
    Args:
        new_targets (List[str]): List of newly detected target IDs
    """
    qr_codes.update_items(new_targets)
    logger.debug(f"Targets updated: {new_targets}")


def validate_server_connection() -> tuple[bool, Optional[str]]:
    """
    Validate that the robot is connected to a game server.
    
    Returns:
        tuple: (is_connected, error_message)
    """
    server_address = get_server_address()
    local_ip = get_local_ip()
    
    if server_address is None:
        return False, "Not connected to any server"
    
    if local_ip is None:
        return False, "Local IP not configured"
    
    return True, None


def has_targets() -> bool:
    """
    Check if any targets are currently available.
    
    Returns:
        bool: True if targets are detected, False otherwise
    """
    return bool(qr_codes.get_items())


def get_primary_target() -> Optional[str]:
    """
    Get the primary (first) detected target.
    
    Returns:
        Optional[str]: Target ID or None if no targets available
    """
    items = qr_codes.get_items()
    if items:
        return items[0]
    return None


@shoot_bp.route('/shoot', methods=['POST'])
def shoot() -> tuple:
    """
    Execute a shot at the current target.
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    global last_shot_time
    
    current_time = time.time()
    
    # Check cooldown
    time_since_last_shot = current_time - last_shot_time
    if time_since_last_shot < SHOOT_COOLDOWN_TIME:
        remaining_cooldown = round(SHOOT_COOLDOWN_TIME - time_since_last_shot, 2)
        logger.debug(f"Shot blocked by cooldown: {remaining_cooldown}s remaining")
        return jsonify({
            "status": "cooldown",
            "message": f"Cooldown in effect. Wait {remaining_cooldown}s"
        }), 200
    
    # Validate server connection
    is_connected, error_msg = validate_server_connection()
    if not is_connected:
        logger.warning(f"Shot blocked: {error_msg}")
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 400
    
    # Check for available targets
    if not has_targets():
        logger.warning("Shot attempted with no targets available")
        return jsonify({
            "status": "error",
            "message": "No targets detected"
        }), 400
    
    # Get target
    target = get_primary_target()
    local_ip = get_local_ip()
    
    logger.info(f"Executing shot at target: {target} from {local_ip}")
    
    # Update cooldown timer
    last_shot_time = current_time
    
    # Prepare and send attack command
    return send_attack_command(target, local_ip)


def send_attack_command(target: str, shooter_ip: str) -> tuple:
    """
    Send an attack command to the game server.
    
    Args:
        target (str): Target ID
        shooter_ip (str): IP address of the shooter
        
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    server_address = get_server_address()
    
    if server_address is None:
        logger.error("Server address is None")
        return jsonify({
            "status": "error",
            "message": "Not connected to server"
        }), 400
    
    # Prepare payload
    payload = {
        "command": f"attack {target} {shooter_ip}"
    }
    
    server_endpoint = f"{server_address}/command"
    
    try:
        logger.debug(f"Sending attack command to {server_endpoint}: {payload}")
        
        response = requests.post(
            server_endpoint,
            json=payload,
            timeout=5
        )
        
        logger.info(f"Server response: {response.status_code}")
        
        try:
            server_response = response.json()
        except ValueError:
            logger.warning(f"Server returned non-JSON response: {response.text}")
            server_response = {"raw_response": response.text}
        
        return jsonify({
            "status": "success",
            "message": f"Attack executed on target {target}",
            "target": target,
            "server_response": server_response
        }), 200
        
    except requests.exceptions.Timeout:
        logger.error("Attack command timed out")
        return jsonify({
            "status": "error",
            "message": "Server connection timed out"
        }), 500
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send attack command: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to contact server: {str(e)}"
        }), 500 
