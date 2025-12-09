"""
Configuration management for R.O.B.E.R.T application.

This module provides centralized configuration management with environment
variable support and type validation.
"""

import os
from typing import Optional, Tuple


class Config:
    """
    Base configuration class for R.O.B.E.R.T.
    
    All configuration values are loaded from environment variables with sensible defaults.
    This allows for easy deployment across different environments without code changes.
    """

    # ==================== Flask Settings ====================
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your_default_secret_key')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() in ('true', '1')

    # ==================== CORS Settings ====================
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')

    # ==================== Camera Settings ====================
    CAMERA_INDEX: int = int(os.getenv('CAMERA_INDEX', 0))
    CAMERA_RESOLUTION: Tuple[int, int] = (640, 480)
    CAMERA_FRAMERATE: int = 30
    JPEG_QUALITY: int = int(os.getenv('JPEG_QUALITY', 15))  # JPEG compression quality (0-100)

    # ==================== Network Monitoring Settings ====================
    NETWORK_CHECK_INTERVAL: int = int(os.getenv('NETWORK_CHECK_INTERVAL', 1))  # Seconds

    # ==================== Motor Settings ====================
    MOTOR_SPEED: float = float(os.getenv('MOTOR_SPEED', 1.0))  # Motor speed multiplier (0.0-1.0)

    # ==================== Flask Server Settings ====================
    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', 5000))
    THREADED: bool = os.getenv('THREADED', 'True').lower() in ('true', '1')

    @classmethod
    def validate(cls) -> None:
        """
        Validate configuration values.
        
        Raises:
            ValueError: If any configuration value is invalid
        """
        if not 0 <= cls.JPEG_QUALITY <= 100:
            raise ValueError("JPEG_QUALITY must be between 0 and 100")
        
        if not 0 <= cls.MOTOR_SPEED <= 1.0:
            raise ValueError("MOTOR_SPEED must be between 0.0 and 1.0")
        
        if cls.SERVER_PORT < 1 or cls.SERVER_PORT > 65535:
            raise ValueError("SERVER_PORT must be between 1 and 65535")
        
        if cls.CAMERA_FRAMERATE < 1 or cls.CAMERA_FRAMERATE > 120:
            raise ValueError("CAMERA_FRAMERATE must be between 1 and 120")

    @classmethod
    def get_camera_config(cls) -> dict:
        """
        Get camera configuration as a dictionary.
        
        Returns:
            dict: Camera configuration parameters
        """
        return {
            'resolution': cls.CAMERA_RESOLUTION,
            'framerate': cls.CAMERA_FRAMERATE,
            'jpeg_quality': cls.JPEG_QUALITY,
            'index': cls.CAMERA_INDEX,
        }

    @classmethod
    def get_server_config(cls) -> dict:
        """
        Get server configuration as a dictionary.
        
        Returns:
            dict: Server configuration parameters
        """
        return {
            'host': cls.SERVER_HOST,
            'port': cls.SERVER_PORT,
            'threaded': cls.THREADED,
            'debug': cls.DEBUG,
        }


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    import logging
    logging.error(f"Configuration validation failed: {e}")
    raise

