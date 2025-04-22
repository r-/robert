from flask import Blueprint, jsonify
from routes.network import get_address
import time
import os
import subprocess
from threading import Lock, Timer
import requests
from tools.RetainedList import RetainedList
from config import Config

shoot_bp = Blueprint('shoot', __name__)

# Cooldown settings
COOLDOWN_TIME = 2
last_shot_time = 0

qr_codes = RetainedList(retention_frames=Config.CAMERA_FRAMERATE, frame_delay=(1/Config.CAMERA_FRAMERATE))
qr_codes.start()


def update_targets(newTargets):
    global qr_codes
    qr_codes.update_items(newTargets)

@shoot_bp.route('/shoot', methods=['POST'])
def shoot():
    global last_shot_time
    global qr_codes

    # Lock and read QR codes safely
    current_time = time.time()

    if current_time - last_shot_time < COOLDOWN_TIME:
        return jsonify({"message": "Cooldown in effect!"}), 200
    
    # Update the last shot time
    last_shot_time = current_time
    items = list(qr_codes.items.keys())
    print(f"QR Codes: {items}")

    if qr_codes.get_items():
        
        qr_data = items[0]
    else:
        print("NO QR code")
        return jsonify({"message": "No QR code detected!"}), 400
    payload = {
        "command": f"attack {qr_data}"
    }

    address = get_address()
    if address is None:
        print("Not connected to server")
        return jsonify({"message": "Not connected to server!"}), 400

    connected_server_address = get_address() + "/command"

    if connected_server_address is None:
        print("No server url")
        return jsonify({"message": "No SERVER_URL found!"}), 200

    try:
        print("Sending request to:", connected_server_address)
        print("Payload:", payload)

        response = requests.post(connected_server_address, json=payload, timeout=5)
        
        print("Server Response Status Code:", response.status_code)
        print("Server Response Text:", response.text)

        server_response = response.json()  # Try to parse JSON response
    except requests.RequestException as e:
        print(e)
        return jsonify({"message": "Failed to send command to server", "error": str(e)}), 500
    except ValueError:
        print(response.text)
        return jsonify({"message": "Server returned invalid JSON", "response": response.text}), 500

    return jsonify({"message": f"Shot fired! QR Code: {qr_data}", "server_response": server_response}), 200
