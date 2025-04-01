from flask import Flask
from flask_cors import CORS
import logging
from config import Config
from routes.chatWithAI import run_chat_ai 
import threading

# Import routes
from routes.camera import camera_bp
from routes.motors import motors_bp
from routes.network import network_bp
from routes.speech import speech_bp
from routes.system import system_bp
from routes.config import config_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})

# Set up logging
log = logging.getLogger('werkzeug')

class NoRequestsFilter(logging.Filter):
    def filter(self, record):
        return not ("GET /" in record.getMessage() or "POST /" in record.getMessage())

log.addFilter(NoRequestsFilter())
log.setLevel(logging.INFO)


# Register Blueprints
app.register_blueprint(camera_bp, url_prefix='/camera')
app.register_blueprint(motors_bp, url_prefix='/motors')
app.register_blueprint(network_bp, url_prefix='/network')
app.register_blueprint(speech_bp, url_prefix='/speech')
app.register_blueprint(config_bp, url_prefix='/config')
app.register_blueprint(system_bp) 

chat_ai_thread = threading.Thread(target=run_chat_ai, daemon=True)
chat_ai_thread.start()

if __name__ == "__main__":
    print(f"Starting server at {app.config['SERVER_HOST']}:{app.config['SERVER_PORT']}")
    app.run(
        host=app.config['SERVER_HOST'],
        port=app.config['SERVER_PORT'],
        threaded=app.config['THREADED']
    )