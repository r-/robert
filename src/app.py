from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from buildhat import Motor
import cv2
import cv2.aruco as aruco

app = Flask(__name__)
CORS(app)

# Initialize motors
# Right engine (forward is positive)
motor_a = Motor('A')

# Left engine (forward is negative due to orientation)
motor_d = Motor('D')

# Global variable for the target ID
target_id = None

# Initialize the camera
camera = cv2.VideoCapture(0)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

@app.route('/control_motor', methods=['POST'])
def control_motor():
    global target_id
    commands = request.json.get('commands', [])
    action = request.json.get('action', 'stop')

    print(f"Received commands: {commands}, action: {action}")

    if action == 'start':
        # Stop both motors first to reset
        motor_a.pwm(0)
        motor_d.pwm(0)

        if 'move_forward' in commands:
            motor_a.pwm(-1)
            motor_d.pwm(1)
        elif 'move_backward' in commands:
            motor_a.pwm(1)
            motor_d.pwm(-1)

        if 'move_left' in commands:
            motor_a.pwm(-1)
            motor_d.pwm(-1)
        elif 'move_right' in commands:
            motor_a.pwm(1)
            motor_d.pwm(1)

    elif action == 'stop':
        print("Stopping motors")
        motor_a.pwm(0)
        motor_d.pwm(0)

    # Ensure target_id is cast to a standard int if it exists
    return jsonify({
        "status": "success",
        "commands": commands,
        "action": action,
        "target_id": int(target_id) if target_id is not None else None
    })
    

@app.route('/video_feed')
def video_feed():
    def generate():
        global target_id
        bounding_box_margin = 60  # Adjust the margin to make the square larger
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            # Frame dimensions and cross position
            height, width, _ = frame.shape
            center_x, center_y = width // 2, height // 2

            # Detect ArUco markers
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            target_id = None  # Reset target_id for each frame
            cross_color = (0, 255, 0)  # Default cross color

            if ids is not None:
                for i, marker_id in enumerate(ids):
                    # Draw rectangle around marker with expanded margin
                    pts = corners[i][0].astype(int)
                    x_min, y_min = pts.min(axis=0)
                    x_max, y_max = pts.max(axis=0)

                    # Expand the bounding box by the margin
                    x_min = max(0, x_min - bounding_box_margin)
                    y_min = max(0, y_min - bounding_box_margin)
                    x_max = min(width, x_max + bounding_box_margin)
                    y_max = min(height, y_max + bounding_box_margin)

                    # Draw the expanded rectangle around the marker
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                    # Display marker ID
                    cv2.putText(frame, f"ID: {marker_id[0]}", (x_min, y_min - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Check if the cross is inside the expanded marker rectangle
                    if x_min < center_x < x_max and y_min < center_y < y_max:
                        cross_color = (0, 0, 255)  # Change cross color to red
                        target_id = int(marker_id[0])  # Cast to standard int

            # Draw green cross in the center of the frame
            cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), cross_color, 2)
            cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), cross_color, 2)

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/activate', methods=['POST'])
def activate():
    """
    Handles activation requests. If a target ID is detected,
    it will return it; otherwise, it indicates no target was found.
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

