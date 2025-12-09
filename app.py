"""
R.O.B.E.R.T Application Entry Point

This module initializes the Flask application, registers all blueprints,
and starts the server with proper logging and configuration management.
"""

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
from routes.dojo import dojo_bp
import threading


class NoRequestsFilter(logging.Filter):
    """Filter to suppress repetitive GET/POST request logs."""
    def filter(self, record):
        """Filter out GET and POST requests to reduce log noise."""
        message = record.getMessage()
        return not ("GET /" in message or "POST /" in message)


def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    log = logging.getLogger('werkzeug')
    # Filter out repeated GET/POST requests to reduce noise
    # Uncomment below if you want to enable this filter
    log.addFilter(NoRequestsFilter())
    log.setLevel(logging.INFO)
    return log


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    # Configure logging
    setup_logging()
    
    return app


def register_blueprints(app: Flask) -> None:
    """
    Register all route blueprints with the application.
    
    Args:
        app (Flask): Flask application instance
    """
    blueprints = [
        (camera_bp, '/camera'),
        (motors_bp, '/motors'),
        (network_bp, '/network'),
        (speech_bp, '/speech'),
        (config_bp, '/config'),
        (shoot_bp, '/shoot'),
        (dojo_bp, '/dojo'),
        (system_bp, ''),  # System blueprint registered without prefix
    ]
    
    for blueprint, prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=prefix)
        logging.debug(f"Registered blueprint {blueprint.name} with prefix '{prefix}'")


def start_ai_thread() -> None:
    """Start the AI chat thread if enabled in configuration."""
    # AI chat functionality has been removed
    logging.info("AI chat functionality is disabled")


def main() -> None:
    """Main entry point for the Flask application."""
    # Create and configure application
    app = create_app()
    
    # Register all blueprints
    register_blueprints(app)
    
    # Start AI service if enabled
    start_ai_thread()
    
    # Log startup information
    logging.info(f"Starting R.O.B.E.R.T server at {app.config['SERVER_HOST']}:{app.config['SERVER_PORT']}")
    
    # Run the Flask application
    app.run(
        host=app.config['SERVER_HOST'],
        port=app.config['SERVER_PORT'],
        threaded=app.config['THREADED'],
        debug=app.config['DEBUG'],
    )


if __name__ == "__main__":
    main()
