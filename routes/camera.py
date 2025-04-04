from flask import Blueprint, Response
import cv2
from threading import Thread, Lock
import time
from config import Config

camera_bp = Blueprint('camera', __name__)

# Initialize camera with settings from Config
camera = cv2.VideoCapture(Config.CAMERA_INDEX)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_RESOLUTION[0])
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_RESOLUTION[1])

frame_lock = Lock()
latest_frame = None

# Initialize the QR Code detector
qr_decoder = cv2.QRCodeDetector()

# List to store detected QR codes
detected_qr_codes = []

def camera_reader():
    global latest_frame
    while True:
        ret, frame = camera.read()
        if ret:
            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect and decode QR codes
            decoded_text, pts, _ = qr_decoder.detectAndDecode(gray_frame)

            if decoded_text and decoded_text not in detected_qr_codes:
                detected_qr_codes.append(decoded_text)  # Store the new QR code data
                print(f"QR Code Detected: {decoded_text}")
                print(f"All Detected QR Codes: {detected_qr_codes}")

            if pts is not None:
                pts = pts.astype(int)  # Convert to integer points
                
                # Draw a bounding box around the QR code
                pts = pts.reshape((-1, 1, 2))  # Reshape for polylines
                cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)  # Green bounding box

                # Draw the decoded text on top of the QR code
                x, y, w, h = cv2.boundingRect(pts)  # Get bounding box coordinates
                cv2.putText(frame, decoded_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            with frame_lock:
                latest_frame = frame

camera_thread = Thread(target=camera_reader, daemon=True)
camera_thread.start()

def generate_mjpeg():
    """Generate MJPEG stream with configured quality."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), Config.JPEG_QUALITY]

    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame, encode_param)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@camera_bp.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')
