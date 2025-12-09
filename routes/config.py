"""
Configuration management routes for R.O.B.E.R.T.

Provides API endpoints to retrieve and modify runtime configuration.
"""

import json
import logging
from flask import Blueprint, request, jsonify
from typing import Tuple, Dict
from config import Config

# Blueprint configuration
config_bp = Blueprint('config', __name__)

# Logger setup
logger = logging.getLogger(__name__)

# Configuration file path
CONFIG_FILE_PATH = 'config.json'


def load_config_from_file() -> Dict:
    """
    Load configuration from the config.json file.
    
    Returns:
        Dict: Configuration dictionary or empty dict if file doesn't exist
    """
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
                logger.info("Configuration loaded from file")
                return config
    except Exception as e:
        logger.warning(f"Failed to load config from file: {e}")
    
    return {}


def save_config_to_file() -> bool:
    """
    Save the current configuration to config.json.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config_dict = {
            "CAMERA_FRAMERATE": Config.CAMERA_FRAMERATE,
            "JPEG_QUALITY": Config.JPEG_QUALITY,
            "MOTOR_SPEED": Config.MOTOR_SPEED
        }
        
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config_dict, f, indent=4)
        
        logger.info("Configuration saved to file")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        return False


@config_bp.route('/get_config', methods=['GET'])
def get_config() -> Tuple[dict, int]:
    """
    Get the current runtime configuration.
    
    Returns:
        tuple: (JSON response with config, HTTP status code)
    """
    try:
        config_data = {
            'CAMERA_FRAMERATE': Config.CAMERA_FRAMERATE,
            'JPEG_QUALITY': Config.JPEG_QUALITY,
            'MOTOR_SPEED': Config.MOTOR_SPEED,
            'CAMERA_RESOLUTION': Config.CAMERA_RESOLUTION,
            'SERVER_HOST': Config.SERVER_HOST,
            'SERVER_PORT': Config.SERVER_PORT,
        }
        logger.debug("Configuration request processed")
        return jsonify(config_data), 200
        
    except Exception as e:
        logger.error(f"Error retrieving configuration: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve configuration"
        }), 500


@config_bp.route('/set_config', methods=['POST'])
def set_config() -> Tuple[dict, int]:
    """
    Update runtime configuration.
    
    Expected JSON payload:
        {
            "framerate": <int>,      # Camera framerate (optional)
            "quality": <int>,        # JPEG quality 0-100 (optional)
            "motor_speed": <float>   # Motor speed multiplier 0-1 (optional)
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    data = request.get_json()
    
    if not data:
        logger.warning("Empty configuration update request")
        return jsonify({
            "status": "error",
            "message": "Request body is empty"
        }), 400
    
    updated_fields = []
    errors = []
    
    # Update framerate
    if 'framerate' in data:
        try:
            framerate = int(data['framerate'])
            if framerate < 1 or framerate > 120:
                errors.append("Framerate must be between 1 and 120")
            else:
                Config.CAMERA_FRAMERATE = framerate
                updated_fields.append('framerate')
                logger.info(f"Updated framerate to {framerate}")
        except (ValueError, TypeError):
            errors.append("Invalid framerate value (must be integer)")
    
    # Update JPEG quality
    if 'quality' in data:
        try:
            quality = int(data['quality'])
            if quality < 0 or quality > 100:
                errors.append("Quality must be between 0 and 100")
            else:
                Config.JPEG_QUALITY = quality
                updated_fields.append('quality')
                logger.info(f"Updated JPEG quality to {quality}")
        except (ValueError, TypeError):
            errors.append("Invalid quality value (must be integer)")
    
    # Update motor speed
    if 'motor_speed' in data:
        try:
            speed = float(data['motor_speed'])
            if speed < 0.0 or speed > 1.0:
                errors.append("Motor speed must be between 0.0 and 1.0")
            else:
                Config.MOTOR_SPEED = speed
                updated_fields.append('motor_speed')
                logger.info(f"Updated motor speed to {speed}")
        except (ValueError, TypeError):
            errors.append("Invalid motor_speed value (must be float)")
    
    # Return error response if there were errors
    if errors and not updated_fields:
        logger.warning(f"Configuration update failed: {errors}")
        return jsonify({
            "status": "error",
            "errors": errors
        }), 400
    
    # Save to file
    save_config_to_file()
    
    response = {
        "status": "success",
        "updated_fields": updated_fields,
        "current_config": {
            'CAMERA_FRAMERATE': Config.CAMERA_FRAMERATE,
            'JPEG_QUALITY': Config.JPEG_QUALITY,
            'MOTOR_SPEED': Config.MOTOR_SPEED
        }
    }
    
    if errors:
        response["warnings"] = errors
    
    logger.info(f"Configuration updated: {updated_fields}")
    return jsonify(response), 200


@config_bp.route('/reset_config', methods=['POST'])
def reset_config() -> Tuple[dict, int]:
    """
    Reset configuration to default values.
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    try:
        Config.CAMERA_FRAMERATE = 30
        Config.JPEG_QUALITY = 15
        Config.MOTOR_SPEED = 1.0
        
        save_config_to_file()
        
        logger.info("Configuration reset to defaults")
        
        return jsonify({
            "status": "success",
            "message": "Configuration reset to defaults",
            "config": {
                'CAMERA_FRAMERATE': Config.CAMERA_FRAMERATE,
                'JPEG_QUALITY': Config.JPEG_QUALITY,
                'MOTOR_SPEED': Config.MOTOR_SPEED
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error resetting configuration: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to reset configuration"
        }), 500


import os

