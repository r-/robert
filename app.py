from flask import Flask, Response, request
import cam
import drive
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Endpoint för kamerastreaming
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Endpoint för motorstyrning via GET-request
@app.route('/control_motor', methods=['GET'])
def control_motor_route():
    motor = request.args.get('motor')
    speed = int(request.args.get('speed'))
    control_motor(motor, speed)
    return f'Motor {motor} set to speed {speed}'

# Endpoint för att stoppa motorerna
@app.route('/stop_motors', methods=['GET'])
def stop_motors_route():
    stop_motors()
    return 'Motors stopped'

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        stop_camera()
        stop_motors()