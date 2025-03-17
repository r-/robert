from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS
from buildhat import Motor
import cv2
import socket
import cv2.aruco as aruco
from threading import Thread, Lock
import time
import pyttsx3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize motors
motor_a = Motor('A')  # Right engine (forward is positive)
motor_d = Motor('D')  # Left engine (forward is negative due to orientation)

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

def generate_mjpeg():
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]  # Lower quality = faster, smaller

    while True:
        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        if frame is None:
            continue
        ret, buffer = cv2.imencode('.jpg', frame, encode_param)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

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
    return render_template('index.html', server_ip=server_ip, latency=trueLatency)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
