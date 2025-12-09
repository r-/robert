"""
Motor control module for R.O.B.E.R.T.

Manages motor operations including drive motors and specialized motors
for camera rotation and continuous rotation tasks.
"""

import threading
import time
import logging
from config import Config
from flask import Blueprint, jsonify, request
from buildhat import Motor
from typing import Optional, Dict

# Blueprint configuration
motors_bp = Blueprint('motors', __name__)

# Logger setup
logger = logging.getLogger(__name__)

# ==================== Motor Initialization ====================
def initialize_motor(port: str, name: str) -> Optional[Motor]:
    """
    Initialize a motor on the specified port.
    
    Args:
        port (str): Motor port letter (A, B, C, D)
        name (str): Human-readable name for the motor
        
    Returns:
        Optional[Motor]: Motor object if successful, None otherwise
    """
    try:
        motor = Motor(port)
        logger.info(f"Motor {port} ({name}) initialized successfully")
        return motor
    except Exception as e:
        logger.error(f"Failed to initialize Motor {port} ({name}): {e}")
        return None


# Initialize all motors
motor_a = initialize_motor('A', 'Right Engine')
motor_d = initialize_motor('D', 'Left Engine')
motor_c = initialize_motor('C', 'Camera Rotation')
motor_b = initialize_motor('B', 'Continuous Rotation')

# Store motors in a dictionary for easier management
motors: Dict[str, Optional[Motor]] = {
    'right_engine': motor_a,
    'left_engine': motor_d,
    'camera_rotation': motor_c,
    'continuous_rotation': motor_b,
}


def check_motor_status(motor: Optional[Motor], motor_name: str) -> str:
    """
    Check and return the status of a motor.
    
    Args:
        motor (Optional[Motor]): Motor object
        motor_name (str): Name of the motor
        
    Returns:
        str: Status message
    """
    if motor is None:
        return f"{motor_name} is NOT initialized (check connection)"
    return f"{motor_name} is initialized and ready"


@motors_bp.route('/get_system_status', methods=['GET'])
def get_system_status() -> tuple:
    """
    Get the status of all motors.
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    system_status = {
        "right_engine": check_motor_status(motor_a, 'Motor A (Right)'),
        "left_engine": check_motor_status(motor_d, 'Motor D (Left)'),
        "camera_rotation": check_motor_status(motor_c, 'Motor C (Camera)'),
        "continuous_rotation": check_motor_status(motor_b, 'Motor B (Continuous)'),
    }
    logger.debug(f"System status requested: {system_status}")
    return jsonify(system_status), 200


@motors_bp.route('/control_motor', methods=['POST'])
def control_motor() -> tuple:
    """
    Control drive motors based on joystick input.
    
    Expected JSON payload:
        {
            "forward": <float>,  # Forward/backward speed (-1.0 to 1.0, positive = forward)
            "right": <float>     # Right/left turning (-1.0 to 1.0, positive = right turn)
        }
    
    Motor mapping:
        - forward = both motors forward/backward
        - right = left motor forward + right motor backward (turns right)
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    data = request.get_json()
    
    if not data or 'forward' not in data or 'right' not in data:
        logger.warning("Invalid motor control request: missing 'forward' or 'right' field")
        return jsonify({
            "status": "error",
            "message": "Invalid request. Required fields: 'forward', 'right'"
        }), 400
    
    try:
        forward_input = float(data['forward'])
        right_input = float(data['right'])
        
        # Apply configuration speed multiplier
        forward_speed = forward_input * Config.MOTOR_SPEED
        right_speed = right_input * Config.MOTOR_SPEED
        
        # Calculate left and right motor speeds
        # forward: move both forward/backward
        # right: turn right (left forward, right backward) or left (left backward, right forward)
        left_motor_speed = forward_speed - right_speed
        right_motor_speed = forward_speed + right_speed
        
        # Clamp speeds to [-1, 1]
        left_motor_speed = max(-1.0, min(1.0, left_motor_speed))
        right_motor_speed = max(-1.0, min(1.0, right_motor_speed))
        
        # Control motors
        if motor_a:
            motor_a.pwm(right_motor_speed)
        if motor_d:
            motor_d.pwm(-left_motor_speed)  # Negative due to motor orientation
        
        logger.debug(f"Motor control: forward={forward_speed:.2f}, right={right_speed:.2f} -> left_motor={left_motor_speed:.2f}, right_motor={right_motor_speed:.2f}")
        
        return jsonify({
            "status": "success",
            "forward_speed": round(forward_speed, 2),
            "right_speed": round(right_speed, 2),
            "left_motor": round(left_motor_speed, 2),
            "right_motor": round(right_motor_speed, 2)
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid motor speed values: {e}")
        return jsonify({
            "status": "error",
            "message": "Invalid speed values. Must be numeric."
        }), 400
    except Exception as e:
        logger.error(f"Motor control error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Motor control failed: {str(e)}"
        }), 500


@motors_bp.route('/control_camera', methods=['POST'])
def control_camera() -> tuple:
    """
    Control camera rotation motor.
    
    Expected JSON payload:
        {
            "up": <float>   # Camera tilt speed (-1.0 to 1.0)
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    data = request.get_json()
    
    if not data or 'up' not in data:
        logger.warning("Invalid camera control request: missing 'up' field")
        return jsonify({
            "status": "error",
            "message": "Invalid request. Required field: 'up'"
        }), 400
    
    try:
        camera_speed = float(data['up'])
        
        # Apply speed scaling: faster forward, slower backward
        if camera_speed > 0:
            camera_speed = 0.2
        else:
            camera_speed = camera_speed * 0.4
        
        # Clamp speed
        camera_speed = max(-1.0, min(1.0, camera_speed))
        
        if motor_c:
            motor_c.pwm(camera_speed)
        
        logger.debug(f"Camera control: speed={camera_speed:.2f}")
        
        return jsonify({
            "status": "success",
            "camera_speed": round(camera_speed, 2)
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid camera speed value: {e}")
        return jsonify({
            "status": "error",
            "message": "Invalid speed value. Must be numeric."
        }), 400
    except Exception as e:
        logger.error(f"Camera control error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Camera control failed: {str(e)}"
        }), 500


def run_continuous_motor() -> None:
    """
    Run the continuous rotation motor at a steady speed.
    
    This function runs in a background thread to maintain continuous rotation
    with periodic updates.
    """
    logger.info("Starting continuous motor rotation")
    try:
        while True:
            if motor_b:
                motor_b.pwm(0.15)  # 15% speed
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Continuous motor interrupted")
    except Exception as e:
        logger.error(f"Error in continuous motor: {e}")
    finally:
        if motor_b:
            motor_b.pwm(0)
            logger.info("Continuous motor stopped")


# Start continuous motor in background thread
continuous_motor_thread = threading.Thread(
    target=run_continuous_motor, 
    daemon=True, 
    name="ContinuousMotor"
)
continuous_motor_thread.start()