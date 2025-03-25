from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS
from buildhat import Motor
import cv2
import socket
import cv2.aruco as aruco
from threading import Thread, Lock
import time
import psutil
import pyttsx3
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

try:
    motor_a = Motor('A')  # Right engine (forward is positive)
except Exception as e:
    print(f"Error initializing Motor A (right-engine). Make sure it's connected to the HAT.")
    motor_a = None

try:
    motor_d = Motor('D')  # Left engine (forward is negative due to orientation)
except Exception as e:
    print(f"Error initializing Motor D (left-engine). Make sure it's connected to the HAT.")
    motor_d = None

try:
    motor_c = Motor('C')  # Camera engine (up & down for rotation)
except Exception as e:
    print(f"Error initializing Motor C. Make sure it's connected to the HAT.")
    motor_c = None

# Global variable for the target ID
target_id = None

engine = pyttsx3.init()
engine.setProperty('volume', 1)  # Volume: 0.0 to 1.0
engine.setProperty('rate', 100)  # Speed: higher is faster

# Initialize the camera
camera = cv2.VideoCapture(0)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

# === Frame buffer & locking ===
latest_frame = None
frame_lock = Lock()

@app.route('/get_system_status', methods=['GET'])
def get_system_status():
    system_status = {
        "Right Engine": check_motor_status(motor_a, 'Motor A'),
        "Left Engine": check_motor_status(motor_d, 'Motor D'),
        "Camera Rotation Engine": check_motor_status(motor_c, 'Motor C'),
        "Camera Feed": check_camera_status(),
    }
    return jsonify(system_status)

def check_motor_status(motor, motor_name):
    """Helper function to check motor status."""
    if motor is None:
        return f"{motor_name} is not initialized. Check the connection."
    else:
        return f"{motor_name} is initialized."

def check_camera_status():
    """Helper function to check camera status."""
    try:
        ret, frame = camera.read()
        if not ret:
            return "Camera is not working. Check the connection."
        else:
            return "Camera is initialized."
    except Exception as e:
        return f"Error with camera: {str(e)}"

def camera_reader():
    global latest_frame
    encode_size = (320, 240)
    while True:
        ret, frame = camera.read()
        if ret:
            frame = cv2.resize(frame, encode_size, interpolation=cv2.INTER_LINEAR)
            with frame_lock:
                latest_frame = frame

# Start camera thread
camera_thread = Thread(target=camera_reader, daemon=True)
camera_thread.start()


# Global variables to store last reading and timestamp
last_net_io = psutil.net_io_counters()
last_time = time.time()

@app.route('/network_speed')
def network_speed():
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

    sent_mbps = (bytes_sent * 8) / (time_diff * 1_000_000)
    recv_mbps = (bytes_recv * 8) / (time_diff * 1_000_000)

    # Update last readings
    last_net_io = current_net_io
    last_time = current_time

    return jsonify({
        "upload_mbps": round(sent_mbps, 2),
        "download_mbps": round(recv_mbps, 2)
    })

@app.route('/control_camera', methods=['POST'])
def control_camera():
    data = request.get_json()
    if not data or 'up' not in data:
        return jsonify({"status": "error", "message": "Invalid camera speed data"}), 400
    camera_speed = float(data['up'])
    if camera_speed <= 0:
        camera_speed *= 0.4
    else:
        camera_speed = 0.2
    try:
        motor_c.pwm(camera_speed)
        return jsonify({"status": "success", "up/down": camera_speed})
    except Exception as e:
        error_message = f"Error controlling camera: {e}"
        return jsonify({"status": "error", "message": error_message}), 500


@app.route('/control_motor', methods=['POST'])
def control_motor():
    """
    Endpoint to control the motors based on joystick input.
    Accepts a JSON payload with 'left' and 'right' motor speeds.
    """
    data = request.get_json()
    if not data or 'left' not in data or 'right' not in data:
        return jsonify({"status": "error", "message": "Invalid motor speed data"}), 400

    left_speed = float(data['left'])
    right_speed = float(data['right'])

    try:
        motor_a.pwm(right_speed)
        motor_d.pwm(-left_speed)
        return jsonify({"status": "success", "left": left_speed, "right": right_speed})
    except Exception as e:
        print(f"Error controlling motors: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Global variables for framerate and JPEG quality
target_fps = 60
jpeg_quality = 10

@app.route('/set_config', methods=['POST'])
def set_config():
    global target_fps, jpeg_quality
    data = request.get_json()

    # Get the new framerate and quality from the request
    target_fps = int(data.get('framerate', target_fps))
    jpeg_quality = int(data.get('quality', jpeg_quality))

    return jsonify({
        "status": "success",
        "framerate": target_fps,
        "quality": jpeg_quality
    })

@app.route('/get_config')
def get_config():
    return jsonify({
        "framerate": target_fps,
        "quality": jpeg_quality
    })

import time
import numpy as np
def generate_mjpeg():
    global target_fps, jpeg_quality
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]  # Use dynamic JPEG quality
    target_size = (640, 480)  # Desired frame resolution
    frame_time = 1.0 / target_fps  # Time per frame in seconds

    prev_frame_time = time.time()  # Time of the last frame sent
    prev_frame = None  # Store the previous frame for difference comparison

    while True:
        current_time = time.time()
        if current_time - prev_frame_time < frame_time:
            continue  # Wait for the right time to process the next frame

        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        
        if frame is None:
            continue  # Skip if no valid frame is available

        resized_frame = cv2.resize(frame, target_size)

        # Frame difference check
        if prev_frame is not None:
            frame_diff = cv2.absdiff(resized_frame, prev_frame)
            non_zero_count = np.count_nonzero(frame_diff)
            if non_zero_count < resized_frame.size * 0.01:
                prev_frame_time = current_time
                continue

        prev_frame = resized_frame  # Update previous frame

        ret, buffer = cv2.imencode('.jpg', resized_frame, encode_param)
        if not ret:
            continue  # Skip if encoding fails

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        prev_frame_time = current_time


@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate', methods=['POST'])
def activate():
    global target_id
    if target_id is not None:
        print(f"Activation request received. Target ID: {target_id}")
        return jsonify({"status": "success", "target_id": int(target_id)})
    else:
        print("Activation request received. No target detected.")
        return jsonify({"status": "success", "target_id": None})
    
@app.route('/say', methods=['POST'])
def talk():
    # Get the message from the incoming JSON request
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Convert the message to speech
    engine.say(message)

    # Wait until speaking is finished
    engine.runAndWait()

    # Return a JSON response
    return jsonify({"message": f"Spoken message: {message}"}), 200

def get_server_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

@app.route('/ping')
def getping():
    try:
        return jsonify(status='OK')
    except Exception as e:
        return jsonify(status='error', message=str(e)), 500

@app.route('/')
def home():
    start_time = time.time()
    server_ip = get_server_ip()
    trueLatency = time.time() - start_time
    print(f"New client connected to: {server_ip}")
    return render_template('index.html', server_ip=server_ip, latency=trueLatency)

if __name__ == "__main__":
    print(f"Successfully started.")
    app.run(host='0.0.0.0', port=5000, threaded=True)
