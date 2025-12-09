"""
Camera control and streaming module for R.O.B.E.R.T.

Handles video feed streaming with ArUco marker detection for QR code recognition
and crosshair overlay for camera alignment.
"""

from flask import Blueprint, Response, jsonify
import cv2
import cv2.aruco as aruco
import numpy as np
from queue import Queue
from config import Config
from routes.shoot import update_targets
import time
from threading import Lock
import atexit
import logging

# Blueprint configuration
camera_bp = Blueprint('camera', __name__)

# Logger setup
logger = logging.getLogger(__name__)

# ==================== Global State ====================
detected_qr_codes = []
qr_codes_lock = Lock()

# ==================== Camera Initialization ====================
camera = cv2.VideoCapture(Config.CAMERA_INDEX)

if not camera.isOpened():
    logger.error(f"Failed to open camera at index {Config.CAMERA_INDEX}")
else:
    logger.info(f"Camera {Config.CAMERA_INDEX} initialized successfully")

# ==================== ArUco Detection Setup ====================
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
aruco_parameters = aruco.DetectorParameters()
qr_decoder = cv2.QRCodeDetector()


def update_camera_settings() -> None:
    """
    Update camera settings from configuration.
    
    Applies resolution, framerate, and FOURCC settings to the camera.
    Logs actual values obtained from the camera.
    """
    logger.info("Updating camera settings")
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_RESOLUTION[0])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_RESOLUTION[1])
    camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FRAMERATE)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    
    # Verify actual settings applied
    actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(camera.get(cv2.CAP_PROP_FPS))
    
    logger.info(f"Requested resolution: {Config.CAMERA_RESOLUTION[0]}x{Config.CAMERA_RESOLUTION[1]}")
    logger.info(f"Actual resolution: {actual_width}x{actual_height}")
    logger.info(f"Requested FPS: {Config.CAMERA_FRAMERATE}, Actual FPS: {actual_fps}")


def detect_aruco_markers(frame: np.ndarray) -> tuple:
    """
    Detect ArUco markers in the frame.
    
    Args:
        frame (np.ndarray): Input frame from camera
        
    Returns:
        tuple: (corners, ids, rejected) - Detection results from ArUco detector
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = aruco.ArucoDetector(aruco_dict, aruco_parameters)
    corners, ids, rejected = detector.detectMarkers(gray)
    return corners, ids, rejected


def draw_marker_bounds(frame: np.ndarray, corners: list, ids: np.ndarray, 
                       marker_id: int, bounding_box_margin: int = 60) -> None:
    """
    Draw bounding boxes and labels around detected markers.
    
    Args:
        frame (np.ndarray): Frame to draw on
        corners (list): List of marker corners
        ids (np.ndarray): Array of marker IDs
        marker_id (int): Index of the marker to draw
        bounding_box_margin (int): Pixel margin around marker
    """
    height, width = frame.shape[:2]
    pts = corners[marker_id][0].astype(int)
    
    # Draw marker outline
    cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    
    # Draw bounding box with margin
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)
    x_min = max(0, x_min - bounding_box_margin)
    y_min = max(0, y_min - bounding_box_margin)
    x_max = min(width, x_max + bounding_box_margin)
    y_max = min(height, y_max + bounding_box_margin)
    
    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.putText(frame, f"ID: {ids[marker_id][0]}", (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


def draw_crosshair(frame: np.ndarray, detected_markers: bool = False) -> None:
    """
    Draw a crosshair at the center of the frame.
    
    Args:
        frame (np.ndarray): Frame to draw on
        detected_markers (bool): If True, draw red crosshair; otherwise green
    """
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    
    # Change color based on detection status
    color = (0, 0, 255) if detected_markers else (0, 255, 0)
    
    cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), color, 2)
    cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), color, 2)


def encode_frame_as_jpeg(frame: np.ndarray) -> bytes:
    """
    Encode a frame as JPEG with configured quality.
    
    Args:
        frame (np.ndarray): Frame to encode
        
    Returns:
        bytes: JPEG-encoded frame
    """
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), Config.JPEG_QUALITY]
    _, buffer = cv2.imencode('.jpg', frame, encode_params)
    return buffer.tobytes()


@camera_bp.route('/detected_qr_codes', methods=['GET'])
def get_detected_qr_codes() -> tuple:
    """
    Get list of currently detected QR codes.
    
    Returns:
        tuple: (JSON response with QR codes, HTTP status code)
    """
    with qr_codes_lock:
        codes = detected_qr_codes.copy()
    
    return jsonify({
        "status": "success",
        "qr_codes": codes
    }), 200


@camera_bp.route('/video_feed')
def video_feed() -> Response:
    """
    Stream video feed with ArUco marker detection and crosshair overlay.
    
    Returns:
        Response: Multipart JPEG stream
    """
    def generate():
        """Generator function for streaming video frames."""
        update_camera_settings()
        logger.info("Starting video feed stream")
        
        try:
            while True:
                ret, frame = camera.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    break
                
                # Clear detected QR codes for this frame
                with qr_codes_lock:
                    detected_qr_codes.clear()
                
                # Detect ArUco markers
                corners, ids, _ = detect_aruco_markers(frame)
                
                # Process detected markers
                if ids is not None:
                    for i, marker_id in enumerate(ids):
                        detected_qr_codes.append(str(marker_id[0]))
                        draw_marker_bounds(frame, corners, ids, i)
                    
                    # Update targets for shoot module
                    with qr_codes_lock:
                        update_targets(detected_qr_codes)
                
                # Draw crosshair (changes color if markers detected)
                draw_crosshair(frame, detected_markers=bool(ids is not None))
                
                # Encode and yield frame
                jpeg_data = encode_frame_as_jpeg(frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg_data + b'\r\n')
                       
        except Exception as e:
            logger.error(f"Error in video feed generation: {e}")
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


def cleanup_camera() -> None:
    """Release camera resources on application shutdown."""
    logger.info("Releasing camera resources")
    if camera.isOpened():
        camera.release()
    logger.info("Camera cleaned up successfully")


# Register cleanup on application exit
atexit.register(cleanup_camera)