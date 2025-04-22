from flask import Blueprint

# Import all route blueprints
from .motors import motors_bp
from .camera import camera_bp
from .network import network_bp
from .system import system_bp
from .speech import speech_bp

# Optionally, you can create a list of all blueprints to register them dynamically
blueprints = [motors_bp, camera_bp, network_bp, system_bp, speech_bp]