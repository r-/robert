import json
from flask import Blueprint, request, jsonify
from config import Config

config_bp = Blueprint('config', __name__)

# Route to get the current configuration
@config_bp.route('/get_config', methods=['GET'])
def get_config():
    config_data = {
        'CAMERA_FRAMERATE': Config.CAMERA_FRAMERATE,
        'JPEG_QUALITY': Config.JPEG_QUALITY,
        'MOTOR_SPEED': Config.MOTOR_SPEED
    }
    return jsonify(config_data)

# Route to update the configuration
@config_bp.route('/set_config', methods=['POST'])
def set_config():
    # Get the data from the request
    data = request.json

    # Update Config class with the new settings
    if 'framerate' in data:
        try:
            Config.CAMERA_FRAMERATE = int(data['framerate'])
        except ValueError:
            return jsonify({"error": "Invalid framerate"}), 400

    if 'quality' in data:
        try:
            Config.JPEG_QUALITY = int(data['quality'])
        except ValueError:
            return jsonify({"error": "Invalid quality"}), 400

    if 'motor_speed' in data:
        try:
            Config.MOTOR_SPEED = float(data['motor_speed'])
        except ValueError:
            return jsonify({"error": "Invalid motor speed"}), 400

    # Optionally, save the updated settings to a config file or .env
    save_config_to_file()

    # Return a success message with the updated config
    return jsonify({
        "status": "success",
        "new_config": {
            'CAMERA_FRAMERATE': Config.CAMERA_FRAMERATE,
            'JPEG_QUALITY': Config.JPEG_QUALITY,
            'MOTOR_SPEED': Config.MOTOR_SPEED
        }
    })


def save_config_to_file():
    """Save the updated configuration to a file (optional)"""
    config_dict = {
        "CAMERA_FRAMERATE": Config.CAMERA_FRAMERATE,
        "JPEG_QUALITY": Config.JPEG_QUALITY,
        "MOTOR_SPEED": Config.MOTOR_SPEED
    }

    with open('config.json', 'w') as f:
        json.dump(config_dict, f, indent=4)

