from flask import Blueprint, jsonify, request
from gtts import gTTS
import os

speech_bp = Blueprint('speech', __name__)

@speech_bp.route('/say', methods=['POST'])
def talk():
    """
    Converts a given text message to speech using Google Text-to-Speech (gTTS)
    and plays it using a system audio player.
    """
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        speak_text(message)

        return jsonify({"message": f"Spoken message: {message}"}), 200
    except Exception as e:
        return jsonify({"error": f"Speech synthesis failed: {str(e)}"}), 500
    

def speak_text(message):
    tts = gTTS(text=message, lang='en', slow=False)
    audio_file = "output.mp3"
    tts.save(audio_file)
    os.system(f"mpg321 {audio_file}")  # Play the audio file