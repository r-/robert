import threading
import time
from config import Config
from flask import Blueprint, jsonify, request
from buildhat import Motor

motors_bp = Blueprint('motors', __name__)

# Initialize motors
try:
    motor_a = Motor('A')  # Right engine (forward is positive)
except Exception as e:
    print(f"Error initializing Motor A (right-engine). Check connection.")
    motor_a = None

try:
    motor_d = Motor('D')  # Left engine (forward is negative due to orientation)
except Exception as e:
    print(f"Error initializing Motor D (left-engine). Check connection.")
    motor_d = None

try:
    motor_c = Motor('C')  # Camera rotation motor
except Exception as e:
    print(f"Error initializing Motor C. Check connection.")
    motor_c = None
    
try:
    motor_b = Motor('B') # Continous rotation motor
except Exception as e:
    print(f"Error initializing Motor B Check connection.")
    motor_b = None

def check_motor_status(motor, motor_name):
    """Helper function to check motor status."""
    if motor is None:
        return f"{motor_name} is not initialized. Check the connection."
    return f"{motor_name} is initialized."

@motors_bp.route('/get_system_status', methods=['GET'])
def get_system_status():
    """Returns the status of the motors."""
    system_status = {
        "Right Engine": check_motor_status(motor_a, 'Motor A'),
        "Left Engine": check_motor_status(motor_d, 'Motor D'),
        "Camera Rotation Engine": check_motor_status(motor_c, 'Motor C'),
        "Continous Rotation Engine": check_motor_status(motor_b, 'Motor B'),
    }
    return jsonify(system_status)

@motors_bp.route('/control_motor', methods=['POST'])
def control_motor():
    """
    Controls the motors based on joystick input.
    Accepts a JSON payload with 'left' and 'right' motor speeds.
    """
    data = request.get_json()
    if not data or 'left' not in data or 'right' not in data:
        return jsonify({"status": "error", "message": "Invalid motor speed data"}), 400

    left_speed = float(data['left']) * Config.MOTOR_SPEED
    right_speed = float(data['right']) * Config.MOTOR_SPEED

    try:
        if motor_a:
            motor_a.pwm(right_speed)
        if motor_d:
            motor_d.pwm(-left_speed)
        return jsonify({"status": "success", "left": left_speed, "right": right_speed})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@motors_bp.route('/control_camera', methods=['POST'])
def control_camera():
    """
    Controls the camera motor.
    Accepts a JSON payload with 'up' (speed for moving up/down).
    """
    data = request.get_json()
    if not data or 'up' not in data:
        return jsonify({"status": "error", "message": "Invalid camera speed data"}), 400

    camera_speed = float(data['up'])
    camera_speed = 0.2 if camera_speed > 0 else camera_speed * 0.4

    try:
        if motor_c:
            motor_c.pwm(camera_speed)
        return jsonify({"status": "success", "up/down": camera_speed})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def run_continuous_motor():
    try:
        while True:
            if motor_b:
                motor_b.pwm(0.15)
            time.sleep(0.1)  # Sleep to avoid CPU overload
    except KeyboardInterrupt:
        # This will handle manual stopping of the program with Ctrl+C
        print("Program interrupted. Stopping motor.")
    finally:
        # Ensure the motor is set to 0 when the program is stopped or encounters an error
        if motor_b:
            motor_b.pwm(0)
            print("Motor stopped.")
threading.Thread(target=run_continuous_motor, daemon=True).start()