from flask import Blueprint, jsonify
from routes.network import get_address
import time
import os
import subprocess
from threading import Lock, Timer
import requests  # Import requests to send HTTP requests

shoot_bp = Blueprint('shoot', __name__)

# Cooldown settings
COOLDOWN_TIME = 2  # seconds
last_shot_time = 0  # last shot time, initialized to 0

qr_codes_lock = Lock()
qr_codes = []

# Update targets with a frame delay to keep them for 15 frames
def update_targets(newTargets):
    global qr_codes
    with qr_codes_lock:
        # Add new targets with a frame count of 0
        qr_codes.extend([(target, 0) for target in newTargets])

def update_frame_counter():
    global qr_codes
    with qr_codes_lock:
        # Increment the frame counter for each QR code
        for i in range(len(qr_codes)):
            qr_code, frame_counter = qr_codes[i]
            qr_codes[i] = (qr_code, frame_counter + 1)

        # Remove QR codes that have been in the list for 15 frames or more
        qr_codes[:] = [qr_code for qr_code, frame_counter in qr_codes if frame_counter < 15]

# Periodically update the frame counter every 100ms (or whatever interval you prefer)
def periodic_update():
    update_frame_counter()
    Timer(0.1, periodic_update).start()  # Schedule the next update in 100ms

# Start the periodic update cycle when the application starts
periodic_update()

@shoot_bp.route('/shoot', methods=['POST'])
def shoot():
    global last_shot_time
    temp_qr = []

    # Lock and read QR codes safely
    with qr_codes_lock:
        temp_qr = [qr_code for qr_code, _ in qr_codes]  # Only take the QR codes (not their frame counters)
    
    current_time = time.time()

    # Check cooldown period
    if current_time - last_shot_time < COOLDOWN_TIME:
        return jsonify({"message": "Cooldown in effect!"}), 200
    # Update the last shot time
    last_shot_time = current_time

    # Debugging: Print previous QR codes
    print(f"QR Codes: {temp_qr}")

    # Get QR code data (assuming previous_qr_codes is a list)
    if temp_qr:
        qr_data = temp_qr[0]  # Use the first detected QR code
    else:
        print("NO QR code")
        return jsonify({"message": "No QR code detected!"}), 400

    # Prepare the request payload
    payload = {
        "command": f"attack {qr_data}"  # Send attack command
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

# Example function for when new QR codes are detected
def on_new_qr_codes(detected_qr_codes):
    update_targets(detected_qr_codes)  # Add new QR codes to the list

