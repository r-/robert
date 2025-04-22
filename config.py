import os

class Config:
    """Base configuration class for R.O.B.E.R.T."""

    # General Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1')

    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Camera settings
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', 0)) 
    CAMERA_RESOLUTION = (640, 480)
    CAMERA_FRAMERATE = 30
    JPEG_QUALITY = int(os.getenv('JPEG_QUALITY', 15))  # JPEG image quality

    # Network monitoring settings
    NETWORK_CHECK_INTERVAL = int(os.getenv('NETWORK_CHECK_INTERVAL', 1))  # Seconds

    # Motor settings
    MOTOR_SPEED = float(os.getenv('MOTOR_SPEED', 1.0))  # Max speed 1.0

    # Speech settings
    SPEECH_ENGINE = os.getenv('SPEECH_ENGINE', 'gtts')  # Options: 'gtts' or 'pyttsx3'

    # Flask server settings
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
    THREADED = os.getenv('THREADED', 'True').lower() in ('true', '1')

    USE_AI = False

