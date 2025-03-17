from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from buildhat import Motor
import cv2
import cv2.aruco as aruco

app = Flask(__name__)
CORS(app)

# Initialize motors
motor_a = Motor('A')  # Right engine (forward is positive)
motor_d = Motor('D')  # Left engine (forward is negative due to orientation)

# Global variable for the target ID
target_id = None

# Initialize the camera
camera = cv2.VideoCapture(0)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

@app.route('/control_motor', methods=['POST'])
def control_motor():
    """
    Endpoint to control the motors based on joystick input.
    Accepts a JSON payload with 'left' and 'right' motor speeds.
    """
    data = request.get_json()
    if not data or 'left' not in data or 'right' not in data:
        return jsonify({"status": "error", "message": "Invalid motor speed data"}), 400

    # Retrieve motor speeds from the request
    left_speed = float(data['left'])
    right_speed = float(data['right'])

    # Print received motor speeds for debugging
    # print(f"Received motor speeds - Left: {left_speed}, Right: {right_speed}")

    # Control the motors with the received speeds
    try:
        motor_a.pwm(right_speed)  # Right motor (invert speed if necessary)
        motor_d.pwm(-left_speed)    # Left motor (invert speed if necessary)
        return jsonify({"status": "success", "left": left_speed, "right": right_speed})
    except Exception as e:
        print(f"Error controlling motors: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def generate_mjpeg():
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        # Resize to smaller resolution to reduce bandwidth
        frame = cv2.resize(frame, (320, 240))

        # Encode with higher compression (lower quality = faster, smaller size)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # 0-100 (lower = more compression)
        ret, buffer = cv2.imencode('.jpg', frame, encode_param)

        # Yield MJPEG formatted frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate', methods=['POST'])
def activate():
    """
    Handles activation requests based on detected ArUco markers.
    """
    global target_id
    if target_id is not None:
        print(f"Activation request received. Target ID: {target_id}")
        return jsonify({"status": "success", "target_id": int(target_id)})
    else:
        print("Activation request received. No target detected.")
        return jsonify({"status": "success", "target_id": None})

if __name__ == "__main__":
    print("Starting Flask app on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
