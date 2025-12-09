"""
Dojo Game Server Integration Module for R.O.B.E.R.T.

Simplified integration: Join game with /JoinGame command, attack via QR codes.
"""

from flask import Blueprint, jsonify, request
import requests
import logging
from typing import Optional, Tuple

# Blueprint configuration
dojo_bp = Blueprint('dojo', __name__)

# Logger setup
logger = logging.getLogger(__name__)

# ==================== Game State ====================
dojo_server_url: Optional[str] = None
player_id: Optional[int] = None
player_code: Optional[int] = None


# ==================== Helper Functions ====================

def is_connected() -> bool:
    """Check if connected to Dojo server."""
    return dojo_server_url is not None and player_id is not None


def join_dojo_server(server_url: str, code: int) -> Tuple[bool, str]:
    """
    Join Dojo server with the given code.
    
    Args:
        server_url (str): Dojo server URL (e.g., "http://localhost:3000")
        code (int): Player code (0-99)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    global dojo_server_url, player_id, player_code
    
    if not 0 <= code <= 99:
        return False, f"Invalid player code: {code} (must be 0-99)"
    
    server_url = server_url.rstrip('/')
    
    try:
        dojo_url = f"{server_url}/api/player/join"
        payload = {"code": code}
        
        logger.info(f"Joining Dojo server at {server_url} with code {code}")
        
        response = requests.post(dojo_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            response_data = response.json()
            pid = response_data.get('playerId') or response_data.get('id')
            
            dojo_server_url = server_url
            player_id = pid
            player_code = code
            
            logger.info(f"Successfully joined Dojo - Player ID: {pid}, Code: {code}")
            return True, f"✅ Joined game! Player ID: {pid}, Code: {code}"
        else:
            return False, f"❌ Server error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "❌ Connection timed out"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"



def attack_player_by_id(target_id: int, damage: int = 20) -> Tuple[bool, str]:
    """
    Attack a player identified by QR code.
    
    Args:
        target_id (int): Target player ID from QR code
        damage (int): Damage amount (default 20)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not is_connected():
        return False, "❌ Not connected to Dojo server. Use /JoinGame first."
    
    try:
        dojo_url = f"{dojo_server_url}/api/player/attack"
        payload = {
            "attackerId": player_id,
            "targetId": target_id,
            "damage": damage
        }
        
        logger.info(f"Attacking player {target_id} for {damage} damage")
        
        response = requests.post(dojo_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            server_response = response.json()
            logger.info(f"Attack successful: {server_response}")
            return True, f"⚔️ Attacked player {target_id}!"
        else:
            return False, f"❌ Attack failed: {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error attacking player: {e}")
        return False, f"❌ Attack error: {str(e)}"




def obtain_flag_by_id(flag_id: int) -> Tuple[bool, str]:
    """
    Obtain a flag (ID 0 or 1) from the game.
    
    Args:
        flag_id (int): Flag ID (0 or 1 for team flags)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not is_connected():
        return False, "❌ Not connected to Dojo server. Use /JoinGame first."
    
    if flag_id not in [0, 1]:
        return False, f"❌ Invalid flag ID: {flag_id} (use 0 or 1)"
    
    try:
        dojo_url = f"{dojo_server_url}/api/flag/obtain"
        payload = {
            "playerId": player_id,
            "flagId": flag_id
        }
        
        logger.info(f"Attempting to obtain flag {flag_id}")
        
        response = requests.post(dojo_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            server_response = response.json()
            logger.info(f"Flag obtained: {server_response}")
            return True, f"🚩 Captured flag {flag_id}!"
        else:
            return False, f"❌ Cannot obtain flag: {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error obtaining flag: {e}")
        return False, f"❌ Error: {str(e)}"




def capture_flag() -> Tuple[bool, str]:
    """
    Capture (deliver) the flag to win.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not is_connected():
        return False, "❌ Not connected to Dojo server. Use /JoinGame first."
    
    try:
        dojo_url = f"{dojo_server_url}/api/flag/capture"
        payload = {"playerId": player_id}
        
        logger.info(f"Attempting to capture flag")
        
        response = requests.post(dojo_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            server_response = response.json()
            logger.info(f"Flag captured: {server_response}")
            return True, f"🎉 Flag captured! Victory!"
        else:
            return False, f"❌ Cannot capture flag: {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error capturing flag: {e}")
        return False, f"❌ Error: {str(e)}"


def get_game_events() -> list:
    """
    Get list of game events from server.
    
    Returns:
        list: Events from the server
    """
    if not is_connected():
        return []
    
    try:
        dojo_url = f"{dojo_server_url}/api/events"
        response = requests.get(dojo_url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
            
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return []


def get_connection_status() -> dict:
    """Get current connection status."""
    return {
        "connected": is_connected(),
        "server": dojo_server_url,
        "player_id": player_id,
        "player_code": player_code
    }


# ==================== Flask Routes ====================

@dojo_bp.route('/status', methods=['GET'])
def status() -> Tuple[dict, int]:
    """Get Dojo connection status."""
    return jsonify(get_connection_status()), 200


@dojo_bp.route('/attack/<int:target_id>', methods=['POST'])
def attack(target_id: int) -> Tuple[dict, int]:
    """Attack a player by ID."""
    data = request.get_json() or {}
    damage = int(data.get('damage', 20))
    
    success, message = attack_player_by_id(target_id, damage)
    
    return jsonify({
        "status": "success" if success else "error",
        "message": message
    }), 200 if success else 400


@dojo_bp.route('/flag/<int:flag_id>/obtain', methods=['POST'])
def obtain_flag(flag_id: int) -> Tuple[dict, int]:
    """Obtain a flag."""
    success, message = obtain_flag_by_id(flag_id)
    
    return jsonify({
        "status": "success" if success else "error",
        "message": message
    }), 200 if success else 400


@dojo_bp.route('/flag/capture', methods=['POST'])
def capture() -> Tuple[dict, int]:
    """Capture the flag."""
    success, message = capture_flag()
    
    return jsonify({
        "status": "success" if success else "error",
        "message": message
    }), 200 if success else 400


@dojo_bp.route('/events', methods=['GET'])
def events() -> Tuple[dict, int]:
    """Get game events."""
    return jsonify({
        "status": "success",
        "events": get_game_events()
    }), 200
