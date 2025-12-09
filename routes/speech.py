"""
Speech synthesis and audio playback module for R.O.B.E.R.T.

Converts text to speech using Google Text-to-Speech and plays audio output.
"""

from flask import Blueprint, jsonify, request
from gtts import gTTS
import os
import logging
from typing import Tuple

# Blueprint configuration
speech_bp = Blueprint('speech', __name__)

# Logger setup
logger = logging.getLogger(__name__)

# Configuration
AUDIO_OUTPUT_FILE = "output.mp3"
AUDIO_PLAYER = "mpg321"  # Audio player command


def speak_text(message: str) -> bool:
    """
    Convert text to speech and play it.
    
    Args:
        message (str): Text message to convert and play
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not message or not isinstance(message, str):
        logger.error(f"Invalid message type or empty message: {message}")
        return False
    
    try:
        # Generate speech
        logger.info(f"Generating speech for: {message[:50]}...")
        tts = gTTS(text=message, lang='en', slow=False)
        
        # Save to file
        tts.save(AUDIO_OUTPUT_FILE)
        logger.debug(f"Audio saved to {AUDIO_OUTPUT_FILE}")
        
        # Play audio
        os.system(f"{AUDIO_PLAYER} {AUDIO_OUTPUT_FILE}")
        logger.info("Audio playback completed")
        
        return True
        
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}")
        return False


@speech_bp.route('/say', methods=['POST'])
def talk() -> Tuple[dict, int]:
    """
    API endpoint to convert text to speech and play it.
    
    Expected JSON payload:
        {
            "message": "<text to speak>"
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    data = request.get_json()
    
    if not data:
        logger.warning("Received empty request body")
        return jsonify({
            "status": "error",
            "message": "Request body is empty"
        }), 400
    
    message = data.get('message', '').strip()
    
    if not message:
        logger.warning("No message provided in request")
        return jsonify({
            "status": "error",
            "message": "No message provided"
        }), 400
    
    # Limit message length for safety
    if len(message) > 500:
        logger.warning(f"Message too long ({len(message)} chars), truncating")
        message = message[:500]
    
    try:
        success = speak_text(message)
        
        if success:
            logger.info(f"Successfully spoke: {message[:50]}...")
            return jsonify({
                "status": "success",
                "message": f"Spoken: {message}"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Speech synthesis failed"
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in speech endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Speech synthesis failed: {str(e)}"
        }), 500