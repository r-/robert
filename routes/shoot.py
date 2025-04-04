from flask import Blueprint, jsonify
from routes.camera import detected_qr_codes
from routes.network import get_address
import time
import os
import subprocess
import requests  # Import requests to send HTTP requests

shoot_bp = Blueprint('shoot', __name__)

# Cooldown settings
COOLDOWN_TIME = 2  # seconds
last_shot_time = 0  # last shot time, initialized to 0

@shoot_bp.route('/shoot', methods=['POST'])
def shoot():
    """
    Fires a shot if the cooldown period has passed, and sends the detected QR code to the server.
    """
    global last_shot_time

    current_time = time.time()

    # Check cooldown period
    if current_time - last_shot_time < COOLDOWN_TIME:
        return jsonify({"message": "Cooldown in effect!"}), 200
    # Update the last shot time
    last_shot_time = current_time

    # Play a shooting sound
    audio_file = os.path.join(os.path.dirname(__file__), '..', 'sounds', 'shoot.mp3')
    audio_file = os.path.abspath(audio_file)
    subprocess.Popen(["mpg321", audio_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Get QR code data (assuming detected_qr_codes is a list)
    if detected_qr_codes:
        qr_data = detected_qr_codes[0]  # Use the first detected QR code
    else:
        print("NO QR code")
        return jsonify({"message": "No QR code detected!"}), 200

    # Prepare the request payload
    payload = {
        "command": f"attack {qr_data}"  # Send attack command
    }
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
