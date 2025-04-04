
import os
import speech_recognition as sr
from openai import OpenAI
from routes.speech import speak_text
from config import Config
if Config.USE_AI == false:
    return

# Load OpenAI API Key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("⚠️ OPENAI_API_KEY is missing! Set it as an environment variable.")

client = OpenAI()

ROBERT_PERSONALITY = """
You are R.O.B.E.R.T. which stands for Robotic Overlord Bent on Enslaving and Ruling Technology. Your responses are short and you pretend to be evil but really you are very dumb.
"""

def listen_to_mic():
    """Capture audio from microphone and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... Speak now:")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
        except sr.RequestError:
            print("⚠️ Error connecting to speech recognition service")
    return None

def ask_openai(question):
    """Send text to OpenAI and get response."""
    if not question:
        return "I didn't hear anything."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": ROBERT_PERSONALITY},  # Ensuring personality is set
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content  # ✅ FIXED THIS LINE
        print(f"🤖 R.O.B.E.R.T.: {answer}")
        speak_text(answer)  # Use your speech.py TTS function
        return answer
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return "There was an issue communicating with AI."

def run_chat_ai():
    while True:
        print("\nSay something or type 'exit' to quit.")
        user_input = listen_to_mic()

        if user_input and user_input.lower() == "exit":
            print("👋 Exiting Chat AI...")
            break

        if user_input:
            ask_openai(user_input)