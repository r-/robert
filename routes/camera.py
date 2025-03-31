from flask import Blueprint, Response
import cv2
from threading import Thread, Lock
from config import Config

camera_bp = Blueprint('camera', __name__)

# Initialize camera with settings from Config
camera = cv2.VideoCapture(Config.CAMERA_INDEX)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_RESOLUTION[0])
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_RESOLUTION[1])

frame_lock = Lock()
latest_frame = None

def camera_reader():
    global latest_frame
    while True:
        ret, frame = camera.read()
        if ret:
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
