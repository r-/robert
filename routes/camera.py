from flask import Blueprint, Response
import cv2
import numpy as np
from threading import Thread
from queue import Queue
from config import Config
import time

camera_bp = Blueprint('camera', __name__)

# Initialize camera with settings from Config
camera = cv2.VideoCapture(Config.CAMERA_INDEX)
if not camera.isOpened():
    raise Exception("Camera could not be opened!")

camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_RESOLUTION[0])
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_RESOLUTION[1])
camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FRAMERATE)  # Set FPS from Config.FPS

# Frame queue to hold only the most recent frame
frame_queue = Queue(maxsize=1)

# Initialize the QR Code detector
qr_decoder = cv2.QRCodeDetector()

# List to store detected QR codes
detected_qr_codes = []

# Use GPU acceleration if available (using CUDA-enabled OpenCV functions)
def camera_reader():
    global latest_frame
    while True:
        ret, frame = camera.read()
        if ret:
            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            _, thresholded = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)

            # Detect and decode QR codes if necessary
            decoded_text, pts, _ = qr_decoder.detectAndDecode(thresholded)

            # Check if QR code is detected and the contour area is valid
            if decoded_text and pts is not None and cv2.contourArea(pts) > 0:
                if decoded_text not in detected_qr_codes:
                    detected_qr_codes.append(decoded_text)  # Store the new QR code data
                    print(f"QR Code Detected: {decoded_text}")
                    print(f"All Detected QR Codes: {detected_qr_codes}")

                # Convert points to integers and draw a bounding box around the QR code
                pts = pts.astype(int)
                pts = pts.reshape((-1, 1, 2))  # Reshape for polylines
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)  # Green bounding box

                # Draw the decoded text on top of the QR code
                x, y, w, h = cv2.boundingRect(pts)
                cv2.putText(frame, decoded_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Put the latest frame into the queue if it's valid
            if not frame_queue.full():
                frame_queue.put(frame)

def generate_mjpeg():
    """Generate MJPEG stream with optimized encoding."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), Config.JPEG_QUALITY]

    while True:
        # Wait until a frame is available in the queue
        if not frame_queue.empty():
            frame = frame_queue.get()  # Get the latest frame from the queue

            # Convert the frame to JPEG format (only when it's needed)
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@camera_bp.route('/video_feed')
def video_feed():
    """Route for streaming MJPEG feed."""
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Graceful shutdown function
def cleanup():
    print("Releasing camera resources...")
    camera.release()

# Add shutdown handling when Flask exits
import atexit
atexit.register(cleanup)

# Start camera reader in a background thread
camera_thread = Thread(target=camera_reader, daemon=True)
camera_thread.start()
