from flask import Flask
from flask_cors import CORS
import logging
from config import Config
from routes.camera import camera_bp
from routes.motors import motors_bp
from routes.network import network_bp
from routes.speech import speech_bp
from routes.system import system_bp
from routes.config import config_bp
from routes.shoot import shoot_bp
import threading

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Set up logging with better configuration#
log = logging.getLogger('werkzeug')

class NoRequestsFilter(logging.Filter):
    def filter(self, record):
        return not ("GET /" in record.getMessage() or "POST /" in record.getMessage())

log.addFilter(NoRequestsFilter())
log.setLevel(logging.INFO)

# Register Blueprints for different routes
app.register_blueprint(camera_bp, url_prefix='/camera')
app.register_blueprint(motors_bp, url_prefix='/motors')
app.register_blueprint(network_bp, url_prefix='/network')
app.register_blueprint(speech_bp, url_prefix='/speech')
app.register_blueprint(config_bp, url_prefix='/config')
app.register_blueprint(shoot_bp, url_prefix='/shoot')
app.register_blueprint(system_bp)

# Thread for AI-related operations
def start_chat_ai():
    from routes.chatWithAI import run_chat_ai  # Lazy import to reduce startup time
    run_chat_ai()

if Config.USE_AI:
    chat_ai_thread = threading.Thread(target=start_chat_ai, daemon=True)
    chat_ai_thread.start()

# Main entry point for the Flask application
if __name__ == "__main__":
    print(f"Starting server at {app.config['SERVER_HOST']}:{app.config['SERVER_PORT']}")
    
    context = (
        'server.crt',
        'server.key',
    )
    
    app.run(
        host=app.config['SERVER_HOST'],
        port=app.config['SERVER_PORT'],
        threaded=app.config['THREADED'],
        ssl_context=context
    )
