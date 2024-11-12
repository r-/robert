from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from buildhat import Motor
import cv2
import cv2.aruco as aruco

app = Flask(__name__)
CORS(app)

# Initialize motors on ports A and D
motor_a = Motor('A')
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
    command = request.json.get('command', '')
    action = request.json.get('action', 'stop')

    if action == 'start':
        if command == 'move_forward':
            motor_a.start(50)
            motor_d.start(50)
        elif command == 'move_backward':
            motor_a.start(-50)
            motor_d.start(-50)
        elif command == 'move_left':
            motor_a.start(-50)
            motor_d.start(50)
        elif command == 'move_right':
            motor_a.start(50)
            motor_d.start(-50)
    elif action == 'stop':
        motor_a.stop()
        motor_d.stop()

    return jsonify({"status": "success", "command": command, "action": action, "target_id": target_id})

@app.route('/video_feed')
def video_feed():
    def generate():
        global target_id
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
                    # Draw rectangle around marker
                    pts = corners[i][0].astype(int)
                    cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

                    # Get marker's bounding box
                    x_min, y_min = pts.min(axis=0)
                    x_max, y_max = pts.max(axis=0)

                    # Display marker ID
                    cv2.putText(frame, f"ID: {marker_id[0]}", (x_min, y_min - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Check if the cross is inside the marker rectangle
                    if x_min < center_x < x_max and y_min < center_y < y_max:
                        cross_color = (0, 0, 255)  # Change cross color to red
                        target_id = marker_id[0]

            # Draw green cross in the center of the frame
            cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), cross_color, 2)
            cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), cross_color, 2)

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

