from flask import Blueprint, Response
import cv2
import numpy as np
from queue import Queue
from config import Config
import cv2.aruco as aruco
from routes.shoot import update_targets
import time
from threading import Lock

qr_codes_lock = Lock()
camera_bp = Blueprint('camera', __name__)

# Initialize camera with settings from Config
camera = cv2.VideoCapture(Config.CAMERA_INDEX)

if not camera.isOpened():
    print("Camera could not be opened!")

# Frame queue to hold only the most recent frame
frame_queue = Queue(maxsize=1)

# List to store detected QR codes
detected_qr_codes = []
qr_codes_lock = Lock()

# Initialize the QR Code detector
qr_decoder = cv2.QRCodeDetector()

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

def update_settings():
    print("Updating settings!")
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_RESOLUTION[0])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_RESOLUTION[1])
    camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FRAMERATE)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
    # Check actual settings
    actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = camera.get(cv2.CAP_PROP_FPS)

    print(f"Requested: {Config.CAMERA_RESOLUTION[0]}x{Config.CAMERA_RESOLUTION[1]} @ {Config.CAMERA_FRAMERATE} FPS")
    print(f"Actual: {actual_width}x{actual_height} @ {actual_fps} FPS")

# Camera feed route
@camera_bp.route('/video_feed')
def video_feed():
    def generate():
        global detected_qr_codes  # Use the global list
        update_settings()

        bounding_box_margin = 60  # Adjust the margin to make the square larger
        while True:
            detected_qr_codes.clear()  # Clear detected QR codes for the current frame
            ret, frame = camera.read()
            if not ret:
                break

            # Frame dimensions and cross position
            height, width, _ = frame.shape
            center_x, center_y = width // 2, height // 2

            # Detect ArUco markers
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detector = aruco.ArucoDetector(aruco_dict, parameters)
            corners, ids, rejected = detector.detectMarkers(gray)

            if ids is not None:
                # Log detected QR Code ID
                for i, marker_id in enumerate(ids):
                    detected_qr_codes.append(f"{marker_id[0]}")

                    # Draw rectangle around marker with expanded margin
                    pts = corners[i][0].astype(int)
                    cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                    x_min, y_min = pts.min(axis=0)
                    x_max, y_max = pts.max(axis=0)
                    x_min = max(0, x_min - bounding_box_margin)
                    y_min = max(0, y_min - bounding_box_margin)
                    x_max = min(width, x_max + bounding_box_margin)
                    y_max = min(height, y_max + bounding_box_margin)
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(frame, f"ID: {marker_id[0]}", (x_min, y_min - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            # Draw green cross in the center of the frame
            cross_color = (0, 255, 0)  # Default cross color
            if detected_qr_codes:  # If QR codes are detected, change the cross color
                cross_color = (0, 0, 255)
            
            # Send the updated list of detected QR codes to the shoot route via update_targets
            with qr_codes_lock:
                update_targets(detected_qr_codes)

            cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), cross_color, 2)
            cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), cross_color, 2)

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), Config.JPEG_QUALITY]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Graceful shutdown function
def cleanup():
    print("Releasing camera resources...")
    camera.release()

# Add shutdown handling when Flask exits
import atexit
atexit.register(cleanup)