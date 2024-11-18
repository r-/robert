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
    left_speed = data['left']
    right_speed = data['right']

    # Print received motor speeds for debugging
    print(f"Received motor speeds - Left: {left_speed}, Right: {right_speed}")

    # Control the motors with the received speeds
    try:
        motor_a.pwm(-right_speed)  # Right motor (invert speed if necessary)
        motor_d.pwm(left_speed)    # Left motor (invert speed if necessary)
        return jsonify({"status": "success", "left": left_speed, "right": right_speed})
    except Exception as e:
        print(f"Error controlling motors: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/video_feed')
def video_feed():
    """
    Stream the camera feed with ArUco marker detection.
    """
    def generate():
        global target_id
        bounding_box_margin = 60
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            # Frame dimensions and center coordinates
            height, width, _ = frame.shape
            center_x, center_y = width // 2, height // 2

            # Detect ArUco markers
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            target_id = None
            cross_color = (0, 255, 0)

            if ids is not None:
                for i, marker_id in enumerate(ids):
                    pts = corners[i][0].astype(int)
                    x_min, y_min = pts.min(axis=0)
                    x_max, y_max = pts.max(axis=0)

                    # Draw rectangle around the marker
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(frame, f"ID: {marker_id[0]}", (x_min, y_min - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Check if crosshair is inside the marker
                    if x_min < center_x < x_max and y_min < center_y < y_max:
                        cross_color = (0, 0, 255)
                        target_id = int(marker_id[0])

            # Draw crosshair
            cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), cross_color, 2)
            cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), cross_color, 2)

            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
    app.run(host='0.0.0.0', port=5000)
